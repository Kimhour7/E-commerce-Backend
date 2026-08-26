from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import uuid

from fastapi import Depends, HTTPException, status, Form
from sqlalchemy import or_
from sqlalchemy.orm import Session
from api.category.schemas import MessageResponse
from api.master_data.otp.models import TBL_USER_OTP
from api.user.models import TBL_USER
from api.user.schemas import UserBase, UserSingleResponse, UserUpdate
from config import configs
from core.db import get_db
from core.securerity import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
    User,
)
from core.permission import AdminPermission
from main import website
import aiosmtplib
from aiosmtplib import SMTPException, SMTPAuthenticationError

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("auth")


#convert TBL_USER row → UserResponse dict
def _user_to_response(user: TBL_USER) -> dict:
    return {
        "id"                : user.id,
        "username"          : user.username,
        "email"             : user.email,
        "first_name"        : user.first_name,
        "last_name"         : user.last_name,
        "phone"             : user.phone,
        "user_role"         : user.user_role,
        "working_company_id": user.working_company_id,
        "working_branch_id" : user.working_branch_id,
        "access_company_id" : user.access_company_id or [],
        "access_branch_id"  : user.access_branch_id or [],
        "created_at"        : user.created_at,
        "updated_at"        : user.updated_at,
    }


#PUBLIC ENDPOINTS
@website.post(
    "/register",
    response_model=MessageResponse,
    summary="Self-register a new account (always 'user' role)",
    tags=["Auth"],
)
def register(
    payload: UserBase,
    db: Session = Depends(get_db),
):
    username = payload.username.strip()

    email = payload.email
    if email:
        email = email.lower().strip()

    existing_user = db.query(TBL_USER).filter(
        TBL_USER.username == username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if email:
        existing_email = db.query(TBL_USER).filter(
            TBL_USER.email == email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    new_user = TBL_USER(
        id         = str(uuid.uuid4()),
        username   = username,
        password   = get_password_hash(payload.password),
        email      = email,
        first_name = payload.first_name,
        last_name  = payload.last_name,
        phone      = payload.phone,
        user_role  = "user",
        access_company_id = [],
        access_branch_id  = [],
        created_by = username,
        updated_by = username,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"User '{username}' registered successfully."
    }


@website.post(
    "/login",
    summary="Login with username & password",
    tags=["Auth"],
)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(TBL_USER).filter(
        TBL_USER.username == username
    ).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    return {
        "access_token" : access_token,
        "refresh_token": refresh_token,
        "token_type"   : "bearer",
    }


#  OTP / PASSWORD RESET
def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

async def _send_otp_email(to_email: str, otp: str) -> None:
    # Validate SMTP configuration
    if not all([configs.SMTP_HOST, configs.SMTP_PORT, configs.SMTP_USERNAME,
                configs.SMTP_PASSWORD, configs.SMTP_FROM]):
        logger.error("Missing SMTP configuration in environment variables")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send OTP email. Missing SMTP configuration.",
        )

    message = MIMEMultipart("alternative")
    message["From"]    = configs.SMTP_FROM
    message["To"]      = to_email
    message["Subject"] = "Your Password Reset OTP"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Password Reset OTP</h2>
        <p>Use the OTP below to reset your password. It expires in <strong>{configs.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
        <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                    background: #f4f4f4; padding: 16px 24px; display: inline-block;
                    border-radius: 8px; margin: 16px 0;">
          {otp}
        </div>
        <p style="color: #888;">If you did not request this, please ignore this email.</p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))

    try:
        smtp_port = int(configs.SMTP_PORT) if isinstance(configs.SMTP_PORT, str) else configs.SMTP_PORT

        logger.info(f"Attempting to send OTP email to {to_email} via {configs.SMTP_HOST}:{smtp_port}")

        use_start_tls = smtp_port == 587
        use_tls       = smtp_port == 465

        async with aiosmtplib.SMTP(
            hostname  = configs.SMTP_HOST,
            port      = smtp_port,
            timeout   = 10,
            start_tls = use_start_tls,
            use_tls   = use_tls
        ) as smtp:
            await smtp.login(configs.SMTP_USERNAME, configs.SMTP_PASSWORD)
            await smtp.send_message(message)

        logger.info(f"OTP email sent successfully to {to_email}")
    except SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SMTP authentication failed. Check your email and password.",
        )
    except SMTPException as e:
        logger.error(f"SMTP error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"SMTP error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Failed to send OTP email: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send OTP email. Check SMTP settings.",
        )

@website.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Send OTP to email for password reset",
    tags=["Auth"],
)
async def forgot_password(
    user_email: str,
    db: Session = Depends(get_db),
):
    user = db.query(TBL_USER).filter(TBL_USER.email == user_email).first()
    if not user:
        return {"message": "If this email is registered, an OTP has been sent."}

    # Delete any existing OTP for this email
    db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == user_email).delete()
    db.commit()

    # Generate new OTP and save to DB
    otp = _generate_otp()
    otp_record = TBL_USER_OTP(
        email=user_email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=configs.OTP_EXPIRE_MINUTES),
    )
    db.add(otp_record)
    db.commit()
    logger.info(f"OTP saved to DB for {user_email}")

    await _send_otp_email(user_email, otp)

    return {"message": "If this email is registered, an OTP has been sent."}


@website.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Verify OTP and set new password",
    tags=["Auth"],
)
async def reset_password(
    user_email  : str,
    user_otp    : str,
    new_password: str,
    db          : Session = Depends(get_db),
):
    record = db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == user_email).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP requested for this email",
        )

    if record.is_expired():
        db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == user_email).delete()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )

    if record.otp != user_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )

    # Update password in DB
    user = db.query(TBL_USER).filter(TBL_USER.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = get_password_hash(new_password)
    db.commit()

    # Clean up OTP
    db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == user_email).delete()
    db.commit()
    logger.info(f"Password reset successfully for {user_email}")

    return {"message": "Password reset successfully. You can now log in with your new password."}


#  AUTHENTICATED ENDPOINTS
@website.get(
    "/me",
    response_model=UserSingleResponse,
    summary="Get current logged-in user profile",
    tags=["Profile"],
)
async def get_me(current_user = Depends(get_current_user)):
    return UserSingleResponse(
        success = True,
        message = "Current user retrieved successfully",
        data    = _user_to_response(current_user),
    )


@website.put(
    "/me",
    response_model=MessageResponse,
    summary="Update own profile (name, email, phone only)",
    tags=["Profile"],
)
async def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    db_user = db.query(TBL_USER).filter(TBL_USER.id == current_user.id).first()

    if payload.email is not None and payload.email != db_user.email:
        existing = db.query(TBL_USER).filter(
            TBL_USER.email == payload.email,
            TBL_USER.id != db_user.id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use by another user",
            )
        db_user.email = payload.email

    if payload.first_name is not None:
        db_user.first_name = payload.first_name
    if payload.last_name is not None:
        db_user.last_name = payload.last_name
    if payload.phone is not None:
        db_user.phone = payload.phone

    db.commit()
    return {"message": "Profile updated successfully"}

#  ADMIN ENDPOINTS (admin / superuser only)
@website.get(
    "/admin/users",
    summary="List all users (paginated)",
    tags=["Admin - User Management"],
)
async def admin_list_users(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
    page        : int     = 1,
    size        : int     = 10,
    search      : str     = None,
    role        : str     = None,
):
    query = db.query(TBL_USER)

    if search:
        query = query.filter(
            or_(
                TBL_USER.username.ilike(f"%{search}%"),
                TBL_USER.email.ilike(f"%{search}%"),
                TBL_USER.first_name.ilike(f"%{search}%"),
                TBL_USER.last_name.ilike(f"%{search}%"),
            )
        )

    if role:
        query = query.filter(TBL_USER.user_role == role)

    # Order by created_at descending
    query = query.order_by(TBL_USER.created_at.desc())

    total_count = query.count()
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()

    return {
        "success"    : True,
        "message"    : "Users retrieved successfully",
        "total"      : total_count,
        "page"       : page,
        "size"       : size,
        "total_pages": (total_count + size - 1) // size if total_count > 0 else 0,
        "data"       : [_user_to_response(u) for u in users],
    }


@website.get(
    "/admin/users/{user_id}",
    response_model=UserSingleResponse,
    summary="Get a user by ID",
    tags=["Admin - User Management"],
)
async def admin_get_user(
    user_id     : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    user = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserSingleResponse(
        success = True,
        message = "User retrieved successfully",
        data    = _user_to_response(user),
    )