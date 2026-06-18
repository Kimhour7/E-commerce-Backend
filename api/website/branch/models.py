from sqlalchemy import Boolean, Column, Date, String, Time
from core.db import CoreAuditModel, Base

class TBL_BRANCH(CoreAuditModel, Base):
    __tablename__ = "tbl_branch"
    
    id           = Column(String(64), primary_key=True, index=True)
    name         = Column(String(250), nullable=False)
    name_lc      = Column(String(250), nullable=False)
    logo         = Column(String(200))
    phone        = Column(String(150))
    telegram     = Column(String(25))
    country_id   = Column(String(64), nullable=False)
    province_id  = Column(String(64), nullable=False)
    district_id  = Column(String(64))
    commune_id   = Column(String(64))
    village_id   = Column(String(64))
    street_no    = Column(String(50))
    lat_long     = Column(String(30))
    opening_date = Column(Date)
    open_hours   = Column(Time)
    close_hours  = Column(Time)
    is_active    = Column(Boolean, default=True)