from sqlalchemy import Column, Integer, String
from core.db import Base

class TBL_ID_COUNTER(Base):
    __tablename__ = "tbl_id_counter"
    
    prefix = Column(String(10), primary_key=True)
    sequence = Column(Integer, nullable=False)