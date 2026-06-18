from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import configs

class RecordStatus(Enum):
    active   = "ACTIVE"
    inactive = "INACTIVE"
    deleted  = "DELETED"

class CoreAuditModel:
    record_status = Column(String, default=RecordStatus.active.value, index=True)
    company_id    = Column(String(255), nullable=True, index=True)
    branch_id     = Column(String(255), nullable=True, index=True)
    created_by    = Column(String, nullable=False)
    updated_by    = Column(String)
    created_at    = Column(DateTime, default=datetime.now)
    updated_at    = Column(DateTime, default=datetime.now)

Base = declarative_base()

engine = create_engine(
    configs.DATABASE_URL,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()