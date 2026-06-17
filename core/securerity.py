from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from api.user.models import TBL_USER
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.db import get_db
from config import configs
from datetime import datetime, timedelta

#================================ Start Hash Password =================================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
#================================== End Hash Password =================================



# ============================== Start Current User Block =============================
class User(BaseModel):
    id                 : str
    username           : str
    first_name         : str | None = None
    last_name          : str | None = None
    email              : str | None = None
    phone              : str | None = None
    user_role          : str | None = None
    is_active          : bool       = True
    working_company_id : str | None = None
    working_branch_id  : str | None = None

    class Config:
        from_attributes = True


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(TBL_USER).filter(TBL_USER.username == username).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )

    return user

# ==============================  End Current User Block ==============================


# ============================== Start Access Token Block =============================

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(days=configs.ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, configs.SECRET_KEY, algorithm=configs.ALGORITHM)

def create_refresh_token(data: dict):
    return jwt.encode(data, configs.SECRET_KEY, algorithm=configs.ALGORITHM)
# =============================== End Access Token Block ==============================
