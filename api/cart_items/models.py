from sqlalchemy import Column, Float, Integer, String

from core.db import AuditTenantMixin, Base


class TBL_CART_ITEMS(AuditTenantMixin, Base):
    __tablename__ = "tbl_cart_items"
    
    id          = Column(String, primary_key=True, unique=True, index=True)
    cart_id     = Column(String(64), nullable=False, index=True)
    product_id  = Column(String(64), nullable=False, index=True)
    company_id  = Column(String(255), nullable=True, index=True)
    branch_id   = Column(String(255), nullable=True, index=True)
    quantity    = Column(Integer, default=1, index=True)
    sub_total   = Column(Float, default=0.00, index=True)