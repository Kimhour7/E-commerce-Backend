from datetime import date
from typing import Optional

from pydantic import BaseModel

class CategoryResponse(BaseModel):
    id: str
    name: str
    photo: Optional[str] = None
    created_by: str
    updated_by: str
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True  # for Pydantic v2

class MessageResponse(BaseModel):
    message: str