from sqlalchemy import Boolean, Column, String, Text
from core.db import CoreAuditModel, Base

class TBL_COUNTRY(CoreAuditModel, Base):
    __tablename__ = "tbl_country"
    
    id      = Column(String(64), primary_key=True, index=True)
    name    = Column(String(100), nullable=False)
    name_lc = Column(String(100), nullable=False)
    note    = Column(String(255))