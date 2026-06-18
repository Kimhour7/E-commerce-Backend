from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import uuid

from fastapi import Depends, HTTPException, status, Form
from sqlalchemy import or_
from sqlalchemy.orm import Session
from api.user.models import TBL_USER
from api.user.schemas import (
    AdminCreateUserRequest,
    AdminUpdateUserRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    UserResponse,
)
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


# ═══════════════════════════════════════════════════════════════════════════════
#  Helper: convert TBL_USER row → UserResponse dict
# ═══════════════════════════════════════════════════════════════════════════════

def _user_to_response(user: TBL_USER) -> dict:
    return {
        "id"                : user.id,
        "username"          : user.username,
        "email"             : user.email,
        "first_name"        : user.first_name,
        "last_name"         : user.last_name,
        "phone"             : user.phone,
        "user_role"         : user.user_role,
        "is_active"         : user.is_active,
        "working_company_id": user.working_company_id,
        "working_branch_id" : user.working_branch_id,
        "created_at"        : str(user.created_at) if user.created_at else None,
        "updated_at"        : str(user.updated_at) if user.updated_at else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  PUBLIC ENDPOINTS (no auth)
# ═══════════════════════════════════════════════════════════════════════════════

@website.post(
    "/register",
    response_model=MessageResponse,
    status_code=201,
    summary="Self-register a new account (always 'user' role)",
    tags=["Auth"],
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    # Check if username already exists
    existing = db.query(TBL_USER).filter(TBL_USER.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    # Check if email already exists (if provided)
    if payload.email:
        existing_email = db.query(TBL_USER).filter(TBL_USER.email == payload.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    new_user = TBL_USER(
        id         = str(uuid.uuid4()),
        username   = payload.username,
        password   = get_password_hash(payload.password),
        email      = payload.email,
        first_name = payload.first_name,
        last_name  = payload.last_name,
        phone      = payload.phone,
        user_role  = "user",  # Always 'user' for self-registration
        is_active  = True,
    )

    db.add(new_user)
    db.commit()

    return {"message": f"User '{payload.username}' registered successfully."}


@website.post(
    "/login",
    response_model=LoginResponse,
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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  OTP / PASSWORD RESET (no auth)
# ═══════════════════════════════════════════════════════════════════════════════

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
        use_tls = smtp_port == 465

        async with aiosmtplib.SMTP(
            hostname=configs.SMTP_HOST,
            port=smtp_port,
            timeout=10,
            start_tls=use_start_tls,
            use_tls=use_tls
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
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(TBL_USER).filter(TBL_USER.email == payload.email).first()
    if not user:
        # Always return success to prevent email enumeration
        return {"message": "If this email is registered, an OTP has been sent."}

    # Delete any existing OTP for this email
    db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == payload.email).delete()
    db.commit()

    # Generate new OTP and save to DB
    otp = _generate_otp()
    otp_record = TBL_USER_OTP(
        email=payload.email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=configs.OTP_EXPIRE_MINUTES),
    )
    db.add(otp_record)
    db.commit()
    logger.info(f"OTP saved to DB for {payload.email}")

    await _send_otp_email(payload.email, otp)

    return {"message": "If this email is registered, an OTP has been sent."}


@website.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Verify OTP and set new password",
    tags=["Auth"],
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    record = db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == payload.email).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP requested for this email",
        )

    if record.is_expired():
        db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == payload.email).delete()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )

    if record.otp != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )

    # Update password in DB
    user = db.query(TBL_USER).filter(TBL_USER.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = get_password_hash(payload.new_password)
    db.commit()

    # Clean up OTP
    db.query(TBL_USER_OTP).filter(TBL_USER_OTP.email == payload.email).delete()
    db.commit()
    logger.info(f"Password reset successfully for {payload.email}")

    return {"message": "Password reset successfully. You can now log in with your new password."}


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATED ENDPOINTS (any logged-in user)
# ═══════════════════════════════════════════════════════════════════════════════

@website.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user profile",
    tags=["Profile"],
)
async def get_me(current_user = Depends(get_current_user)):
    return _user_to_response(current_user)


@website.put(
    "/me",
    response_model=MessageResponse,
    summary="Update own profile (name, email, phone only)",
    tags=["Profile"],
)
async def update_me(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    db_user = db.query(TBL_USER).filter(TBL_USER.id == current_user.id).first()

    # Check email uniqueness if changing
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


@website.put(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Change own password",
    tags=["Profile"],
)
async def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    db_user = db.query(TBL_USER).filter(TBL_USER.id == current_user.id).first()

    if not verify_password(payload.current_password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    db_user.password = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN ENDPOINTS (admin / superuser only)
# ═══════════════════════════════════════════════════════════════════════════════

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
    is_active   : bool    = None,
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

    if is_active is not None:
        query = query.filter(TBL_USER.is_active == is_active)

    # Order by created_at descending (newest first)
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
    response_model=UserResponse,
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
    return _user_to_response(user)


@website.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user (admin can assign any role)",
    tags=["Admin - User Management"],
)
async def admin_create_user(
    payload     : AdminCreateUserRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    # Check username uniqueness
    existing = db.query(TBL_USER).filter(TBL_USER.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    # Check email uniqueness if provided
    if payload.email:
        existing_email = db.query(TBL_USER).filter(TBL_USER.email == payload.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    # Validate role
    valid_roles = ["user", "manager", "admin", "superuser"]
    if payload.user_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    new_user = TBL_USER(
        id                 = str(uuid.uuid4()),
        username           = payload.username,
        password           = get_password_hash(payload.password),
        email              = payload.email,
        first_name         = payload.first_name,
        last_name          = payload.last_name,
        phone              = payload.phone,
        user_role          = payload.user_role,
        is_active          = True,
        working_company_id = payload.working_company_id,
        working_branch_id  = payload.working_branch_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return _user_to_response(new_user)


@website.put(
    "/admin/users/{user_id}",
    response_model=MessageResponse,
    summary="Update a user (admin can change role, active status)",
    tags=["Admin - User Management"],
)
async def admin_update_user(
    user_id     : str,
    payload     : AdminUpdateUserRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    db_user = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check email uniqueness if changing
    if payload.email is not None and payload.email != db_user.email:
        existing = db.query(TBL_USER).filter(
            TBL_USER.email == payload.email,
            TBL_USER.id != user_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use by another user",
            )

    # Validate role if changing
    if payload.user_role is not None:
        valid_roles = ["user", "manager", "admin", "superuser"]
        if payload.user_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
            )

    if payload.email is not None:
        db_user.email = payload.email
    if payload.first_name is not None:
        db_user.first_name = payload.first_name
    if payload.last_name is not None:
        db_user.last_name = payload.last_name
    if payload.phone is not None:
        db_user.phone = payload.phone
    if payload.user_role is not None:
        db_user.user_role = payload.user_role
    if payload.is_active is not None:
        db_user.is_active = payload.is_active
    if payload.working_company_id is not None:
        db_user.working_company_id = payload.working_company_id
    if payload.working_branch_id is not None:
        db_user.working_branch_id = payload.working_branch_id

    db.commit()
    return {"message": "User updated successfully"}


@website.delete(
    "/admin/users/{user_id}",
    response_model=MessageResponse,
    summary="Delete a user",
    tags=["Admin - User Management"],
)
async def admin_delete_user(
    user_id     : str,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(AdminPermission),
):
    db_user = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-deletion
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}