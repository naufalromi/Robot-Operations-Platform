from sqlalchemy import Column, Float, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    battery = Column(Float)
    status = Column(String)
    x = Column(Float)
    y = Column(Float)
    task = Column(String, nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
