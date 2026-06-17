from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ============================== Auth Schemas ==============================

class RegisterRequest(BaseModel):
    username  : str
    password  : str
    email     : EmailStr | None = None
    first_name: str | None = None
    last_name : str | None = None
    phone     : str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token : str
    refresh_token: str | None = None
    token_type   : str
    expires_in   : int | None = None

class MessageResponse(BaseModel):
    message: str


# ============================== Password Schemas ==============================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email       : EmailStr
    otp         : str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password    : str


# ============================== User Response Schemas ==============================

class UserResponse(BaseModel):
    id                : str
    username          : str
    email             : str | None = None
    first_name        : str | None = None
    last_name         : str | None = None
    phone             : str | None = None
    user_role         : str | None = None
    is_active         : bool       = True
    working_company_id: str | None = None
    working_branch_id : str | None = None
    created_at        : str | None = None
    updated_at        : str | None = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    success    : bool
    message    : str
    total      : int
    page       : int
    size       : int
    total_pages: int
    data       : List[UserResponse]


# ============================== Self-Update Schema ==============================

class UpdateProfileRequest(BaseModel):
    email     : EmailStr | None = None
    first_name: str | None = None
    last_name : str | None = None
    phone     : str | None = None


# ============================== Admin User Schemas ==============================

class AdminCreateUserRequest(BaseModel):
    username          : str
    password          : str
    email             : EmailStr | None = None
    first_name        : str | None = None
    last_name         : str | None = None
    phone             : str | None = None
    user_role         : str = "user"
    working_company_id: str | None = None
    working_branch_id : str | None = None

class AdminUpdateUserRequest(BaseModel):
    email             : EmailStr | None = None
    first_name        : str | None = None
    last_name         : str | None = None
    phone             : str | None = None
    user_role         : str | None = None
    is_active         : bool | None = None
    working_company_id: str | None = None
    working_branch_id : str | None = None
