from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base Schemas and Create
class CompanyBase(BaseModel):
    name          : str                = Field(..., max_length=250)
    name_lc       : str                = Field(..., max_length=250)
    description   : Optional[str]      = None
    description_lc: Optional[str]      = None
    logo          : Optional[str]      = Field(None, max_length=200)
    banner        : Optional[str]      = Field(None, max_length=200)
    phone         : Optional[str]      = Field(None, max_length=150)
    telegram      : Optional[str]      = Field(None, max_length=25)
    email         : Optional[EmailStr] = Field(None, max_length=100)
    facebook      : Optional[str]      = Field(None, max_length=100)
    youtube       : Optional[str]      = Field(None, max_length=100)
    country_id    : str                = Field(..., max_length=64)
    province_id   : str                = Field(..., max_length=64)
    district_id   : Optional[str]      = Field(None, max_length=64)
    commune_id    : Optional[str]      = Field(None, max_length=64)
    village_id    : Optional[str]      = Field(None, max_length=64)
    street_no     : Optional[str]      = Field(None, max_length=50)
    lat_long      : Optional[str]      = Field(None, max_length=30)

# Update 
class CompanyUpdate(BaseModel):
    name          : Optional[str]      = Field(None, max_length=250)
    name_lc       : Optional[str]      = Field(None, max_length=250)
    description   : Optional[str]      = None
    description_lc: Optional[str]      = None
    logo          : Optional[str]      = Field(None, max_length=200)
    banner        : Optional[str]      = Field(None, max_length=200)
    phone         : Optional[str]      = Field(None, max_length=150)
    telegram      : Optional[str]      = Field(None, max_length=25)
    email         : Optional[EmailStr] = Field(None, max_length=100)
    facebook      : Optional[str]      = Field(None, max_length=100)
    youtube       : Optional[str]      = Field(None, max_length=100)
    country_id    : Optional[str]      = Field(None, max_length=64)
    province_id   : Optional[str]      = Field(None, max_length=64)
    district_id   : Optional[str]      = Field(None, max_length=64)
    commune_id    : Optional[str]      = Field(None, max_length=64)
    village_id    : Optional[str]      = Field(None, max_length=64)
    street_no     : Optional[str]      = Field(None, max_length=50)
    lat_long      : Optional[str]      = Field(None, max_length=30)

# Lightweight schema for list views / dropdowns
class CompanyBrief(BaseModel):
    id       : str
    name     : str
    logo     : Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

#Response
class CompanyResponse(BaseModel):
    id            : str
    name          : str
    name_lc       : str
    description   : Optional[str] = None
    description_lc: Optional[str] = None
    logo          : Optional[str] = None
    banner        : Optional[str] = None
    phone         : Optional[str] = None
    telegram      : Optional[str] = None
    email         : Optional[EmailStr] = None
    facebook      : Optional[str] = None
    youtube       : Optional[str] = None
    country_id    : str
    province_id   : str
    district_id   : Optional[str] = None
    commune_id    : Optional[str] = None
    village_id    : Optional[str] = None
    street_no     : Optional[str] = None
    lat_long      : Optional[str] = None
    record_status : Optional[str] = None
    created_by    : Optional[str] = None
    updated_by    : Optional[str] = None
    created_at    : Optional[datetime] = None
    updated_at    : Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CompanySingleResponse(BaseModel):
    success : bool
    message : str
    data    : Optional[CompanyResponse] = None

    model_config = ConfigDict(from_attributes=True)

class CompanyListResponse(BaseModel):
    success     : bool
    message     : str
    total       : Optional[int] = None
    page        : Optional[int] = None
    size        : Optional[int] = None
    total_pages : Optional[int] = None
    data        : List[CompanyResponse]

    model_config = ConfigDict(from_attributes=True)
