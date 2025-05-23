from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from app.database import Base

class JejuTransport(Base):
    __tablename__ = "transport"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), default="transport")
    x_cord = Column(Float, default=0.0)
    y_cord = Column(Float, default=0.0)
    open_time = Column(String(50), default="")
    close_time = Column(String(50), default="")
    service_time = Column(Integer, default=0)
    tags = Column(JSON, nullable=True)
    closed_days = Column(JSON, nullable=True)
    break_time = Column(JSON, nullable=True)
    is_mandatory = Column(Boolean, default=False)
    address = Column(String(255), default="")
    phone = Column(String(50), default="")
    convenience = Column(String(255), default="")
    website = Column(String(255), default="")
    image_url = Column(Text, nullable=True)