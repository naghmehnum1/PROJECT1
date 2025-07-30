from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Ad(Base):
    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    publish_date = Column(String, nullable=True)
    area = Column(String, nullable=True)
    price = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    num_rooms = Column(String, nullable=True)
    meterage = Column(String, nullable=True)
    year_built = Column(String, nullable=True)
    crawled_at = Column(DateTime, nullable=True) 
