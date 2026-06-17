from sqlalchemy import Column, Float, String

from core.db import AuditTenantMixin, Base


class TBL_CART(AuditTenantMixin, Base):
    __tablename__ = "tbl_cart"
    
    id          = Column(String, primary_key=True, unique=True, index=True)
    user_id     = Column(String(64), nullable=False, index=True)
    company_id  = Column(String(255), nullable=True, index=True)
    branch_id   = Column(String(255), nullable=True, index=True)
    total_price = Column(Float, default=0.00, index=True)
    status      = Column(String(20), default="PENDING") #PENDING PAID CANCEL