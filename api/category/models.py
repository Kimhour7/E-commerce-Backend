from sqlalchemy import Column, Integer, String
from core.db import CoreAuditModel, Base

class TBL_CATEGORY(CoreAuditModel, Base):
    __tablename__ = "tbl_category"
    
    id           = Column(String, primary_key=True, unique=True, index=True)
    name         = Column(String, nullable=False)
    photo        = Column(String(255), nullable=True)