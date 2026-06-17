from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from core.db import Base


class TBL_USER_OTP(Base):
    __tablename__ = "tbl_user_otp"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    email      = Column(String, nullable=False, index=True)
    otp        = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at



class TBL_ID_COUNTER(Base):
    __tablename__ = "tbl_id_counter"

    prefix = Column(String(10), primary_key=True)  # e.g. "PRO", "CAT"
    sequence = Column(Integer, nullable=False)


class TBL_USER(Base):
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

    created_at         = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)