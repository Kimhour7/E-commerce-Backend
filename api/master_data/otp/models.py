from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
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
