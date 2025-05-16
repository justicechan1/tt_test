# router/maps.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import re
from datetime import datetime
from typing import List
from app.cache import user_schedules
from app.database import get_db

from app.models.jeju_cafe import JejuCafe, JejuCafeHashtag
from app.models.jeju_restaurant import JejuRestaurant, JejurestaurantHashtag
from app.models.jeju_tourism import JejuTourism, JejutourismHashtag
from app.models.jeju_hotel import JejuHotel, JejuhotelHashtag

from app.schemas.maps import (
    HashtagInput, HashtagOutput, TagInfo,
    MoveInput, MoveResponse, MoveInfo,
    RouteInput, RouteResponse, VisitInfo
)

from TripScheduler.tripscheduler.scheduler_api import schedule_trip

router = APIRouter(prefix="/api/users/maps", tags=["maps"])

PLACE_MODELS = {
    "cafe": (JejuCafe, JejuCafeHashtag),
    "restaurant": (JejuRestaurant, JejurestaurantHashtag),
    "tourism": (JejuTourism, JejutourismHashtag),
    "hotel": (JejuHotel, JejuhotelHashtag)
}

PRIMARY_KEY_FIELDS = {
    "cafe": "cafe_id",
    "restaurant": "restaurant_id",
    "tourism": "tourism_id",
    "hotel": "hotel_id"
}

# ---------- /hashtage ----------
@router.post("/hashtage", response_model=HashtagOutput)
def get_hashtags(input_data: HashtagInput, db: Session = Depends(get_db)):
    category = input_data.category.lower()
    viewport = input_data.viewport

    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")

    PlaceModel, HashtagModel = PLACE_MODELS[category]
    pk_field = getattr(PlaceModel, PRIMARY_KEY_FIELDS[category])
    fk_field = getattr(HashtagModel, PRIMARY_KEY_FIELDS[category])

    subquery = db.query(pk_field).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).subquery()

    hashtag_rows = db.query(HashtagModel.hashtag_name).filter(
        fk_field.in_(subquery)
    ).all()

    unique_tags = set()
    for row in hashtag_rows:
        if not row.hashtag_name:
            continue
        try:
            tags = re.findall(r'\["(#[^"]+)"\]', row.hashtag_name)
            unique_tags.update(tags)
        except:
            continue

    return HashtagOutput(tag=[TagInfo(hashtag_name=tag) for tag in unique_tags])

# ---------- /move ----------
@router.post("/move", response_model=MoveResponse)
def get_move_candidates(input_data: MoveInput, db: Session = Depends(get_db)):
    tags = [t.hashtag_name for t in input_data.tag]
    viewport = input_data.viewport
    results = []

    for category, (PlaceModel, HashtagModel) in PLACE_MODELS.items():
        pk_field_name = PRIMARY_KEY_FIELDS[category]
        pk_field = getattr(PlaceModel, pk_field_name)
        fk_field = getattr(HashtagModel, pk_field_name)

        subquery = db.query(pk_field).filter(
            PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
            PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
        ).subquery()

        tagged_ids = db.query(fk_field).filter(
            fk_field.in_(subquery),
            HashtagModel.hashtag_name.isnot(None)
        ).all()

        for place_id, in tagged_ids:
            hashtag_entry = db.query(HashtagModel).filter(
                getattr(HashtagModel, pk_field_name) == place_id
            ).first()
            if not hashtag_entry or not hashtag_entry.hashtag_name:
                continue

            try:
                place_tags = re.findall(r'\["(#[^"]+)"\]', hashtag_entry.hashtag_name)
                if not any(tag in place_tags for tag in tags):
                    continue
            except:
                continue

            place = db.query(PlaceModel).filter(pk_field == place_id).first()
            if place:
                results.append(MoveInfo(
                    name=place.name,
                    x_cord=float(place.x_cord),
                    y_cord=float(place.y_cord)
                ))

    return MoveResponse(move=results)

# ---------- 경로 결과 포맷 변환 ----------
def convert_to_move_response(data: dict) -> RouteResponse:
    visits = [VisitInfo(**v) for v in data.get("visits", [])]
    path = [[[p[0], p[1]] for p in segment] for segment in data.get("path", [])]
    return RouteResponse(visits=visits, path=path)

# ---------- 사용자 일정 정보 가져오기 ----------
def get_day_info(user_id: str, target_date: str) -> dict:
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="사용자 일정이 존재하지 않습니다.")

    date_range = user_schedules[user_id]["date"]
    start_date = date_range.start_date
    end_date = date_range.end_date

    weekday_index = datetime.strptime(target_date, "%Y-%m-%d").weekday()
    weekdays_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

    return {
        "is_first_day": target_date == start_date,
        "is_last_day": target_date == end_date,
        "date": target_date,
        "weekday": weekdays_kor[weekday_index]
    }

# ---------- route 입력을 위한 dict 구성 ----------
def build_schedule_input(user_id: str, target_date: str, db: Session) -> dict:
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="사용자 일정이 존재하지 않습니다.")

    schedule_data = user_schedules[user_id]
    places_by_day = schedule_data["places_by_day"]
    user_info = schedule_data["user"]

    if target_date not in places_by_day:
        raise HTTPException(status_code=404, detail=f"{target_date}에 해당하는 장소 데이터가 없습니다.")

    place_objs: List[dict] = []
    for place in places_by_day[target_date]:
        place_name = place["name"] if isinstance(place, dict) else place.name

        for category, (PlaceModel, _) in PLACE_MODELS.items():
            db_place = db.query(PlaceModel).filter(
                func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place_name))
            ).first()
            if db_place:
                place_objs.append({
                    "id": db_place.id,
                    "name": db_place.name,
                    "x_cord": float(db_place.x_cord),
                    "y_cord": float(db_place.y_cord),
                    "category": category,
                    "open_time": db_place.open_time or "00:00",
                    "close_time": db_place.close_time or "23:59",
                    "service_time": int(db_place.service_time or 0),
                    "tags": getattr(db_place, "tags", []) or [],
                    "closed_days": getattr(db_place, "closed_days", []) or [],
                    "break_time": getattr(db_place, "break_time", []) or [],
                    "is_mandatory": getattr(db_place, "is_mandatory", False)
                })
                break

    return {
        "places": place_objs,
        "user": user_info.dict(),
        "day_info": get_day_info(user_id, target_date)
    }

# ---------- /route ----------
@router.post("/route", response_model=RouteResponse)
def get_optimal_route(input_data: RouteInput, db: Session = Depends(get_db)):
    # 1. 사용자 입력 기반 일정 구성
    input_dict = build_schedule_input(
        user_id=input_data.user_id,
        target_date=input_data.date,
        db=db
    )

    # 경로 최적화 알고리즘 실행
    result = schedule_trip(input_dict)

    #/init_show 데이터 갱신
    ordered_place_names = [visit["place"] for visit in result.get("visits", [])]
    original_places = user_schedules[input_data.user_id]["places_by_day"][input_data.date]
    name_to_place = {
        place.name if not isinstance(place, dict) else place["name"]: place
        for place in original_places
    }
    reordered_places = [
        name_to_place[name] for name in ordered_place_names if name in name_to_place
    ]
    user_schedules[input_data.user_id]["places_by_day"][input_data.date] = reordered_places
    user_schedules[input_data.user_id].setdefault("optimized_orders", {})[input_data.date] = ordered_place_names

    return convert_to_move_response(result)