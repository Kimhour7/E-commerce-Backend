from sqlalchemy import Boolean, Column, String
from core.db import CoreAuditModel, Base

class TBL_USER(CoreAuditModel, Base):
    __tablename__ = "tbl_user"
    
    id                 = Column(String(36), primary_key=True)
    username           = Column(String(255), nullable=False, unique=True, index=True)
    password           = Column(String(255), nullable=True)
    email              = Column(String(255), nullable=True)
    first_name         = Column(String(255), nullable=True)
    last_name          = Column(String(255), nullable=True)
    phone              = Column(String(50), nullable=True)
    user_role          = Column(String(50), default="user", nullable=False)
    is_active          = Column(Boolean, default=True, nullable=False)
    working_company_id = Column(String(255), nullable=True)
    working_branch_id  = Column(String(255), nullable=True)