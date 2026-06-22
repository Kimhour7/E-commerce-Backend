from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base Schemas and Create
class BranchBase(BaseModel):
    name         : str            = Field(..., max_length=250)
    name_lc      : str            = Field(..., max_length=250)
    logo         : Optional[str]  = Field(None, max_length=200)
    phone        : Optional[str]  = Field(None, max_length=150)
    telegram     : Optional[str]  = Field(None, max_length=25)
    country_id   : str            = Field(..., max_length=64)
    province_id  : str            = Field(..., max_length=64)
    district_id  : Optional[str]  = Field(None, max_length=64)
    commune_id   : Optional[str]  = Field(None, max_length=64)
    village_id   : Optional[str]  = Field(None, max_length=64)
    street_no    : Optional[str]  = Field(None, max_length=50)
    lat_long     : Optional[str]  = Field(None, max_length=30)
    opening_date : Optional[date] = Field(None)
    open_hours   : Optional[time] = Field(None)
    close_hours  : Optional[time] = Field(None)

# Update 
class BranchUpdate(BaseModel):
    name         : Optional[str]  = Field(None, max_length=250)
    name_lc      : Optional[str]  = Field(None, max_length=250)
    logo         : Optional[str]  = Field(None, max_length=200)
    phone        : Optional[str]  = Field(None, max_length=150)
    telegram     : Optional[str]  = Field(None, max_length=25)
    country_id   : Optional[str]  = Field(None, max_length=64)
    province_id  : Optional[str]  = Field(None, max_length=64)
    district_id  : Optional[str]  = Field(None, max_length=64)
    commune_id   : Optional[str]  = Field(None, max_length=64)
    village_id   : Optional[str]  = Field(None, max_length=64)
    street_no    : Optional[str]  = Field(None, max_length=50)
    lat_long     : Optional[str]  = Field(None, max_length=30)
    opening_date : Optional[date] = Field(None)
    open_hours   : Optional[time] = Field(None)
    close_hours  : Optional[time] = Field(None)

#Response
class BranchResponse(BaseModel):
    id           : str
    company_id   : str
    name         : str
    name_lc      : str
    logo         : Optional[str] = None
    phone        : Optional[str] = None
    telegram     : Optional[str] = None
    country_id   : str
    province_id  : str
    district_id  : Optional[str] = None
    commune_id   : Optional[str] = None
    village_id   : Optional[str] = None
    street_no    : Optional[str] = None
    lat_long     : Optional[str] = None
    opening_date : Optional[date]= None
    open_hours   : Optional[time]= None
    close_hours  : Optional[time]= None
    record_status: Optional[str] = None
    created_by   : Optional[str] = None
    updated_by   : Optional[str] = None
    created_at   : Optional[datetime] = None
    updated_at   : Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class BranchSingleResponse(BaseModel):
    success : bool
    message : str
    data    : Optional[BranchResponse] = None

    model_config = ConfigDict(from_attributes=True)

class BranchListResponse(BaseModel):
    success     : bool
    message     : str
    total       : Optional[int] = None
    page        : Optional[int] = None
    size        : Optional[int] = None
    total_pages : Optional[int] = None
    data        : List[BranchResponse]

    model_config = ConfigDict(from_attributes=True)