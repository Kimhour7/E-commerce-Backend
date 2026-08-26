from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

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
    access_company_id  : List[str]     = Field(default_factory=list)
    access_branch_id   : List[str]     = Field(default_factory=list)

# Update
class UserUpdate(BaseModel):
    first_name         : Optional[str]       = Field(None, max_length=250)
    last_name          : Optional[str]       = Field(None, max_length=250)
    username           : Optional[str]       = Field(None, max_length=250)
    password           : Optional[str]       = Field(None, max_length=250)
    email              : Optional[str]       = Field(None, max_length=200)
    phone              : Optional[str]       = Field(None, max_length=150)
    user_role          : Optional[str]       = Field(None, max_length=25)
    working_company_id : Optional[str]       = Field(None, max_length=64)
    working_branch_id  : Optional[str]       = Field(None, max_length=64)
    access_company_id  : Optional[List[str]] = None
    access_branch_id   : Optional[List[str]] = None

#Response
class UserResponse(BaseModel):
    id                 : Optional[str] = Field(None, max_length=64)
    first_name         : Optional[str] = Field(None, max_length=250)
    last_name          : Optional[str] = Field(None, max_length=250)
    username           : Optional[str] = Field(None, max_length=250)
    email              : Optional[str] = Field(None, max_length=200)
    phone              : Optional[str] = Field(None, max_length=150)
    user_role          : Optional[str] = Field(None, max_length=25)
    working_company_id : Optional[str] = Field(None, max_length=64)
    working_branch_id  : Optional[str] = Field(None, max_length=64)
    access_company_id  : List[str]     = Field(default_factory=list)
    access_branch_id   : List[str]     = Field(default_factory=list)
    created_at         : Optional[datetime] = None
    updated_at         : Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserSingleResponse(BaseModel):
    success : bool
    message : str
    data    : Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
