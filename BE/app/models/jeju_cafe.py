from sqlalchemy import Column, Integer, String, Float, Text, DECIMAL, JSON
from app.database import Base

class JejuCafe(Base):
    __tablename__ = "cafe"

    cafe_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    category = Column(String(255))
    page_url = Column(Text)
    score = Column(Float)
    address = Column(Text)
    phone = Column(String(100))
    convenience = Column(Text)
    website = Column(Text)
    y_cord = Column(DECIMAL(10, 7))
    x_cord = Column(DECIMAL(10, 7))
    open_time = Column(String(255))
    close_time = Column(String(255))
    break_time = Column(String(255))
    service_time = Column(String(255))
    closed_days = Column(String(255))
    image_url = Column(Text)

    @property
    def id(self):
        return self.cafe_id

    class Config:
        orm_mode = True

class JejuCafeHashtag(Base):
    __tablename__ = "jeju_cafe_hashtags"

    id = Column(Integer, primary_key=True)  
    cafe_id = Column(Integer)
    name = Column(String(100))
    hashtage_name = Column(String(100))  
    embeddings = Column(JSON)

    class Config:
        orm_mode = True
