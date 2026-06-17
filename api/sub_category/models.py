from sqlalchemy import Column, String
from core.db import AuditTenantMixin, Base

class TBL_SUB_CATEGORY(AuditTenantMixin, Base):
    __tablename__ = "tbl_sub_category"
    
    id           = Column(String, primary_key=True, unique=True, index=True)
    category_id  = Column(String, index=True)
    name         = Column(String, nullable=False)
    photo        = Column(String(255), nullable=True)