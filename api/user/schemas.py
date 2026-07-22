from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base Schemas and Create
class UserBase(BaseModel):
    first_name         : str           = Field(..., max_length=250)
    last_name          : str           = Field(..., max_length=250)
    username           : str           = Field(..., max_length=250)
    password           : str           = Field(..., max_length=250)
    email              : str           = Field(..., max_length=200)
    phone              : Optional[str] = Field(None, max_length=150)
    user_role          : Optional[str] = Field(None, max_length=25)
    working_company_id : Optional[str] = Field(None, max_length=64)
    working_branch_id  : Optional[str] = Field(None, max_length=64)

# Update 
class UserUpdate(BaseModel):
    first_name         : Optional[str] = Field(None, max_length=250)
    last_name          : Optional[str] = Field(None, max_length=250)
    username           : Optional[str] = Field(None, max_length=250)
    password           : Optional[str] = Field(None, max_length=250)
    email              : Optional[str] = Field(None, max_length=200)
    phone              : Optional[str] = Field(None, max_length=150)
    user_role          : Optional[str] = Field(None, max_length=25)
    working_company_id : Optional[str] = Field(None, max_length=64)
    working_branch_id  : Optional[str] = Field(None, max_length=64)

#Response
class UserResponse(BaseModel):
    first_name         : Optional[str] = Field(None, max_length=250)
    last_name          : Optional[str] = Field(None, max_length=250)
    username           : Optional[str] = Field(None, max_length=250)
    password           : Optional[str] = Field(None, max_length=250)
    email              : Optional[str] = Field(None, max_length=200)
    phone              : Optional[str] = Field(None, max_length=150)
    user_role          : Optional[str] = Field(None, max_length=25)
    working_company_id : Optional[str] = Field(None, max_length=64)
    working_branch_id  : Optional[str] = Field(None, max_length=64)

    model_config = ConfigDict(from_attributes=True)

class UserSingleResponse(BaseModel):
    success : bool
    message : str
    data    : Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)