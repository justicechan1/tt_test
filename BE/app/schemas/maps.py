# schemas/maps.py

from pydantic import BaseModel
from typing import List, Optional

# ---------- 해시태그 (Hashtage) ----------

class TagInfo(BaseModel):
    hashtage_name: str

class Viewport(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class HashtagInput(BaseModel):
    category: str
    viewport: Viewport

class HashtagOutput(BaseModel):
    tag: List[TagInfo]

# ---------- 지도 새로고침 (Move) ----------

class MoveInfo(BaseModel):
    name: str
    x_cord: float
    y_cord: float

class MoveInput(BaseModel):
    tag: List[TagInfo]
    viewport: Viewport

class MoveResponse(BaseModel):
    move: List[MoveInfo]

# ---------- 경로 최적화 (Route) ----------

class RouteInput(BaseModel):
    user_id: str
    date: int

class VisitInfo(BaseModel):
    order: int
    place: str
    arrival_str: str
    departure_str: str
    stay_duration: str
    x_cord: float
    y_cord: float
    travel_time: Optional[str] = None
    wait_time: Optional[str] = None

class RouteResponse(BaseModel):
    visits: List[VisitInfo]
    path: List[List[List[float]]]

# ---------- 내부 데이터 구조 (for /route 내부 처리용) ----------

class MapPlaceDetailOutput(BaseModel):
    id: int
    name: str
    x_cord: float
    y_cord: float
    category: str
    open_time: str
    close_time: str
    service_time: int
    tags: List[str]
    closed_days: List[str]
    break_time: List[str]
    is_mandatory: bool

class DayInfo(BaseModel):
    is_first_day: bool
    is_last_day: bool
    date: str
    weekday: str
