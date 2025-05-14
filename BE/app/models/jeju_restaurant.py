<<<<<<< HEAD
#models\main_restaurant.py
from sqlalchemy import Column, Integer, String, Float, Text, DECIMAL
from app.database import Base

class jeju_restaurant(Base):
    __tablename__ = "jeju_restaurant"

    id = Column(Integer, primary_key=True, autoincrement=True)
=======
#models/jeju_restaurant.py
from sqlalchemy import Column, Integer, String, Float, Text, DECIMAL
from app.database import Base

class JejuRestaurant(Base):
    __tablename__ = "jeju_restaurant"

    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
>>>>>>> cace62f (tt_test_v3)
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
<<<<<<< HEAD
=======
    image_url = Column(Text)

    @property
    def id(self):
        return self.restaurant_id
>>>>>>> cace62f (tt_test_v3)

    class Config:
        orm_mode = True

<<<<<<< HEAD
class JejuRestaurantImage(Base):
    __tablename__ = "jeju_restaurant_image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))  # jeju_restaurant.name과 연동 키
    url_1 = Column(String(500))
    url_2 = Column(String(500))
    url_3 = Column(String(500))
    url_4 = Column(String(500))
    url_5 = Column(String(500))
    url_6 = Column(String(500))

    class Config:
        orm_mode = True

class JejuRestaurantHashtag(Base):
    __tablename__ = "jeju_restaurant_hashtags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    hashtag_name = Column(String)

    class Config:
        orm_mode = True
=======
class JejurestaurantHashtag(Base):
    __tablename__ = "jeju_restaurant_hashtags"  

    restaurant_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    hashtag_name = Column(Text)  

    class Config:
        orm_mode = True
>>>>>>> cace62f (tt_test_v3)
