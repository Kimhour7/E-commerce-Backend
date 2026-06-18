from sqlalchemy import Boolean, Column, String, Text
from core.db import CoreAuditModel, Base

class TBL_PROVINCE(CoreAuditModel, Base):
    __tablename__ = "tbl_province"
    
    id         = Column(String(64), primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    name_lc    = Column(String(100), nullable=False)
    country_id = Column(String(64))
    image      = Column(String(200))