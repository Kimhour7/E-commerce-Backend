from sqlalchemy import Boolean, Column, String, Text
from core.db import CoreAuditModel, Base

class TBL_COMPANY(CoreAuditModel, Base):
    __tablename__ = "tbl_company"
    
    id             = Column(String(64), primary_key=True, index=True)
    name           = Column(String(250), nullable=False)
    name_lc        = Column(String(250), nullable=False)
    description    = Column(Text())
    description_lc = Column(Text())
    logo           = Column(String(200))
    banner         = Column(String(200))
    phone          = Column(String(150))
    telegram       = Column(String(25))
    email          = Column(String(100))
    facebook       = Column(String(100))
    youtube        = Column(String(100))
    country_id     = Column(String(64), nullable=False)
    province_id    = Column(String(64), nullable=False)
    district_id    = Column(String(64))
    commune_id     = Column(String(64))
    village_id     = Column(String(64))
    street_no      = Column(String(50))
    lat_long       = Column(String(30))