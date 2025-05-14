#schemas/maps.py
from pydantic import BaseModel, RootModel
from typing import List, Dict

# 공통

class TagInfo(BaseModel):
    hashtag_name: str

class MoveInfo(BaseModel):
    name: str
    x_cord: float
    y_cord: float

class Viewport(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class PathPoint(BaseModel):
    x: float
    y: float

class PathInfo(RootModel[List[PathPoint]]):
    pass

# 해시태그

class HashtagInput(BaseModel):
    category: str
    viewport: Viewport

class HashtagOutput(BaseModel):
    tag: List[TagInfo]

# 지도 새로고침

class MoveInput(BaseModel):
    tag: List[TagInfo]
    viewport: Viewport

class MoveResponse(BaseModel):
    move: List[MoveInfo]

# 경로 최적화

class VisitInfo(BaseModel):
    order: int
    place: str
    arrival_str: str
    departure_str: str
    stay_duration: str
    x_cord: float
    y_cord: float
    travel_time: str | None = None
    wait_time: str | None = None

class RouteResponse(BaseModel):
    visits: List[VisitInfo]
    path: List[List[List[float]]]
