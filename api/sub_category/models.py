from sqlalchemy import Column, String
from core.db import CoreAuditModel, Base

class TBL_SUB_CATEGORY(CoreAuditModel, Base):
    __tablename__ = "tbl_sub_category"
    
    id           = Column(String, primary_key=True, unique=True, index=True)
    category_id  = Column(String, index=True)
    name         = Column(String, nullable=False)
    photo        = Column(String(255), nullable=True)