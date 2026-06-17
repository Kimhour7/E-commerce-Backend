from sqlalchemy import Boolean, Column, Float, Integer, String, Text

from core.db import AuditTenantMixin, Base


class TBL_PRODUCT(AuditTenantMixin, Base):
    __tablename__ = "tbl_product"
    
    id                  = Column(String, primary_key=True, unique=True, index=True)
    category_id         = Column(String(64), nullable=False, index=True)
    sub_category_id     = Column(String(64), nullable=False, index=True)
    product_tag_id      = Column(String(64), nullable=False, index=True)
    name                = Column(String(100), nullable=False)
    stock               = Column(Integer, nullable=False, index=True)
    price               = Column(Float, nullable=False, index=True)
    percentage_discount = Column(Integer, default=0)
    description         = Column(Text)
    photo               = Column(String(255))
    active              = Column(Boolean, default=True)