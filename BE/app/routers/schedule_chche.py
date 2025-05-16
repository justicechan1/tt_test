#router/schedule_chche.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from typing import Dict, List
from datetime import datetime
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tourism import JejuTourism
from app.models.jeju_hotel import JejuHotel
from app.cache import user_schedules
from app.schemas import (
    ScheduleInitInput, ScheduleInitOutput,
    ScheduleShowInput, ScheduleShowOutput,
    PlaceSimpleInput, PlaceDetailOutput, PlaceInfoOutputByDay
)

router = APIRouter(prefix="/api/users/schedules", tags=["Schedule"])

PLACE_MODELS = {
    "cafe": (JejuCafe),
    "restaurant": (JejuRestaurant),
    "tourism": (JejuTourism),
    "hotel": (JejuHotel)
}

# ---------- /init ----------
@router.post("/init", response_model=ScheduleInitOutput)
def init_schedule(input_data: ScheduleInitInput, db: Session = Depends(get_db)):
    user_id = input_data.date.user_id

    user_schedules[user_id] = {
        "date": input_data.date,
        "start_end": input_data.start_end,
        "user": input_data.user,
        "places_by_day": {}
    }
    enriched_places_by_day = {}

    for date, places in input_data.places_by_day.items():
        enriched_places = []

        for place in places:
            for category, PlaceModel in PLACE_MODELS.items():
                db_place = db.query(PlaceModel).filter(
                    func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place.name))
                ).first()

                if db_place:
                    enriched_places.append(PlaceDetailOutput(
                        id=db_place.id,
                        name=db_place.name,
                        x_cord=float(db_place.x_cord),
                        y_cord=float(db_place.y_cord),
                        category=category,
                        open_time=db_place.open_time or "",
                        close_time=db_place.close_time or "",
                        service_time=int(db_place.service_time or 0),
                        tags=getattr(db_place, "tags", []) or [],
                        closed_days=getattr(db_place, "closed_days", []) or [],
                        break_time=getattr(db_place, "break_time", []) or [],
                        is_mandatory=getattr(db_place, "is_mandatory", False)
                    ))
                    break

        enriched_places_by_day[date] = enriched_places

    user_schedules[user_id]["places_by_day"] = enriched_places_by_day

    return ScheduleInitOutput(
        date=input_data.date,
        start_end=input_data.start_end,
        places_by_day=enriched_places_by_day
    )

# ---------- /init_show ----------
@router.get("/init_show", response_model=ScheduleShowOutput)
def show_schedule(user_id: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="해당 사용자의 일정이 존재하지 않습니다.")

    schedule_data = user_schedules[user_id]
    date_info = schedule_data["date"]
    start_end_info = schedule_data["start_end"]
    stored_places_by_day = schedule_data["places_by_day"]

    result_places_by_day = {}

    start_date = datetime.strptime(date_info.start_date, "%Y-%m-%d")

    # 날짜 정렬
    for date_str in sorted(stored_places_by_day.keys()):
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        day_index = (current_date - start_date).days + 1
        day_key = f"Day {day_index}"  

        day_places = []

        for place in stored_places_by_day[date_str]:
            place_name = place["name"] if isinstance(place, dict) else place.name

            for category, PlaceModel in PLACE_MODELS.items():
                db_place = db.query(PlaceModel).filter(
                    func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place_name))
                ).first()

                if db_place:
                    image_urls = db_place.image_url.split(",") if db_place.image_url else []

                    day_places.append(
                        PlaceInfoOutputByDay(
                            name=db_place.name,
                            address=db_place.address,
                            phone=getattr(db_place, "phone", ""),
                            convenience=getattr(db_place, "convenience", ""),
                            category=category,
                            website=getattr(db_place, "website", ""),
                            business_hours=None,
                            open_time=db_place.open_time or "",
                            close_time=db_place.close_time or "",
                            image_urls=image_urls
                        )
                    )
                    break

        result_places_by_day[day_key] = day_places

    return ScheduleShowOutput(
        date=date_info,
        start_end=start_end_info,
        places_by_day=result_places_by_day  
    )