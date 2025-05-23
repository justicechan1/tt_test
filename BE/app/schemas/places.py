#schemas/places.py
from pydantic import BaseModel
from typing import List, Optional, Dict


# ------------------- /api/places/edit -------------------
class PlaceNameOnly(BaseModel):
    name: str

class PlaceEditInput(BaseModel):
    user_id: str
    places_by_day: Dict[int, List[PlaceNameOnly]]

class PlaceEditOutput(BaseModel):
    places_by_day: Dict[int, List[PlaceNameOnly]]

# ------------------- /api/places/search -------------------
class PlaceSearchResult(BaseModel):
    name: str

class PlaceSearchOutput(BaseModel):
    search: List[PlaceSearchResult]

# ------------------- /api/places/data -------------------
class PlaceDataResult(BaseModel):
    name: str
    address: str
    x_cord: Optional[float] = None  
    y_cord: Optional[float] = None
    close_time: Optional[str] = None
    phone: Optional[str] = None
    convenience: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    business_hours: Optional[str] = None
    open_time: Optional[str] = None
    image_urls: List[str] = None

    class Config:
        orm_mode = True

class PlaceDataResponse(BaseModel):
    places: PlaceDataResult