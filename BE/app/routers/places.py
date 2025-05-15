#router/places.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from sqlalchemy import or_ 
from sqlalchemy import func
from app.database import get_db
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tourism import JejuTourism
from app.models.jeju_hotel import JejuHotel
from app.cache import user_schedules
from app.schemas.places import (
    PlaceSearchOutput, PlaceSearchResult,PlaceNameOnly,
    PlaceDataResponse, PlaceDataResult,
    PlaceEditInput, PlaceEditOutput,PlaceDetailOutput
)

import re

router = APIRouter(prefix="/api/places", tags=["places"])

# 장소 모델만 등록 (image_model은 따로 필요 없음)
PLACE_MODELS = {
    "cafe": JejuCafe,
    "restaurant": JejuRestaurant,
    "tourism": JejuTourism,
    "hotel": JejuHotel
}

# 이미지 URL 추출 함수
def fetch_image_urls(db: Session, model, name: str) -> list[str]:
    db_place = db.query(model).filter(
        func.trim(func.lower(model.name)) == func.trim(func.lower(name))
    ).first()
    if not db_place or not db_place.image_url:
        return []

    try:
        # ["url1"]["url2"]... 형식에서 URL만 추출
        return re.findall(r'\["(https?://[^"]+)"\]', db_place.image_url)
    except Exception as e:
        print(f"[이미지 파싱 오류]: {e}")
        return []

#  장소 검색

@router.get("/search", response_model=PlaceSearchOutput)
def search_places(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    search_term = f"%{name.strip()}%"
    results = []

    for model_type, model in PLACE_MODELS.items():
        try:
            matches = db.query(model).filter(
                or_(
                    func.lower(model.name).like(func.lower(search_term)),
                    func.lower(getattr(model, "category", "")).like(func.lower(search_term))
                )
            ).all()

            for match in matches:
                results.append(PlaceSearchResult(name=match.name))
        except Exception as e:
            print(f"[{model_type}] 검색 중 오류 발생: {str(e)}")

    return PlaceSearchOutput(search=results)


#  장소 상세 정보 조회
@router.get("/data", response_model=PlaceDataResponse)
def get_place_detail(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    place_name = name.strip()
    for _, model in PLACE_MODELS.items():
        place = db.query(model).filter(model.name == place_name).first()
        if place:
            image_urls = fetch_image_urls(db, model, place_name)
            return PlaceDataResponse(
                places=PlaceDataResult(
                    name=place.name,
                    address=place.address,
                    phone=getattr(place, "phone", None),
                    convenience=getattr(place, "convenience", None),
                    category=getattr(place, "category", None),
                    website=getattr(place, "website", None),
                    business_hours=getattr(place, "business_hours", None),
                    open_time=getattr(place, "open_time", None),
                    close_time=getattr(place, "close_time", None),
                    image_urls=image_urls
                )
            )
    raise HTTPException(status_code=404, detail="해당 장소는 데이터베이스에 존재하지 않습니다.")

# 날짜 변환(Day1~DayN)
def convert_to_day_keys(places_by_day: Dict[str, List], start_date_str: str) -> Dict[str, List[PlaceNameOnly]]:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    result = {}
    for date_str in sorted(places_by_day.keys()):
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        day_index = (current_date - start_date).days + 1
        day_key = f"Day {day_index}"
        result[day_key] = [
            PlaceNameOnly(name=p["name"] if isinstance(p, dict) else p.name)
            for p in places_by_day[date_str]
        ]
    return result

#  일정에 장소 추가
@router.post("/add", response_model=PlaceEditOutput)
def add_place(input_data: PlaceEditInput, user_id: str = Query(...), db: Session = Depends(get_db)):
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="해당 사용자의 일정이 존재하지 않습니다.")

    user_data = user_schedules[user_id]

    for date, places in input_data.places_by_day.items():
        if date not in user_data["places_by_day"]:
            user_data["places_by_day"][date] = []

        existing_names = {
            p["name"] if isinstance(p, dict) else p.name
            for p in user_data["places_by_day"][date]
        }

        for place in places:
            place_name = place.name.strip()

            if place_name in existing_names:
                raise HTTPException(
                    status_code=409,
                    detail=f"{date}에 이미 '{place_name}'이(가) 일정에 존재합니다."
                )

            # DB에 존재하는지 확인
            db_match = None
            for Model in PLACE_MODELS.values():
                db_place = db.query(Model).filter(
                    func.trim(func.lower(Model.name)) == func.trim(func.lower(place_name))
                ).first()
                if db_place:
                    db_match = db_place
                    break

            if not db_match:
                raise HTTPException(status_code=404, detail=f"'{place_name}'은(는) 데이터베이스에 존재하지 않습니다.")

            user_data["places_by_day"][date].append({"name": place_name})

    return PlaceEditOutput(
        places_by_day=convert_to_day_keys(user_data["places_by_day"], user_data["date"].start_date)
    )

#  일정에서 장소 제거
@router.post("/remove", response_model=PlaceEditOutput)
def remove_place(input_data: PlaceEditInput, user_id: str = Query(...)):
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="해당 사용자의 일정이 존재하지 않습니다.")

    user_data = user_schedules[user_id]

    for date, places in input_data.places_by_day.items():
        if date not in user_data["places_by_day"]:
            raise HTTPException(status_code=404, detail=f"{date} 일정이 존재하지 않습니다.")

        scheduled_places = user_data["places_by_day"][date]
        scheduled_names = {
            p["name"] if isinstance(p, dict) else p.name
            for p in scheduled_places
        }

        for place in places:
            place_name = place.name.strip()

            if place_name not in scheduled_names:
                raise HTTPException(
                    status_code=404,
                    detail=f"{date} 일정에 '{place_name}'이(가) 존재하지 않습니다."
                )

            user_data["places_by_day"][date] = [
                p for p in scheduled_places
                if (p["name"] if isinstance(p, dict) else p.name) != place_name
            ]

    return PlaceEditOutput(
        places_by_day=convert_to_day_keys(user_data["places_by_day"], user_data["date"].start_date)
    )