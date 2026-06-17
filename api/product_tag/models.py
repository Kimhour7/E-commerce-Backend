from datetime import datetime

from sqlalchemy import Column, DateTime, String
from core.db import Base

class TBL_PRODUCT_TAG(Base):
    __tablename__ = "tbl_product_tag"
    
    id           = Column(String, primary_key=True, unique=True, index=True)
    name         = Column(String, nullable=False)
    
    created_by   = Column(String, nullable=False)
    updated_by   = Column(String, nullable=False)
    created_at   = Column(DateTime, default=datetime.now)
    updated_at   = Column(DateTime, default=datetime.now)