#router/schedule_chche.py
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from datetime import datetime, timedelta
from app.models.jeju_cafe import JejuCafe
from app.models.jeju_restaurant import JejuRestaurant
from app.models.jeju_tourism import JejuTourism
from app.models.jeju_hotel import JejuHotel
from app.models.jeju_transport import JejuTransport
from app.cache import user_schedules
from app.schemas import (
    ScheduleInitInput, ScheduleInitOutput,
    EditServiceTimeInput, ScheduleShowOutput,
    EditServiceTimeOutput, PlaceDetailOutput, PlaceInfoOutputByDay,
    PlaceWithTime
)

router = APIRouter(prefix="/api/users/schedules", tags=["Schedule"])

PLACE_MODELS = {
    "cafe": (JejuCafe),
    "restaurant": (JejuRestaurant),
    "tourism": (JejuTourism),
    "hotel": (JejuHotel),
    "transport": (JejuTransport)
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

    start_date = input_data.date.start_date
    end_date = input_data.date.end_date

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    day_count = (end_dt - start_dt).days + 1

    for i in range(day_count):
        day_index = i + 1
        date = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        places = input_data.places_by_day.get(day_index, [])
        enriched_places = []

        # 1. 도착지 추가 (첫날 맨 앞)
        if date == start_date:
            arrival_name = input_data.start_end.arrival
            for category, PlaceModel in PLACE_MODELS.items():
                db_place = db.query(PlaceModel).filter(
                    func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(arrival_name))
                ).first()
                if db_place:
                    enriched_places.append(PlaceDetailOutput(
                        id=db_place.id,
                        name=db_place.name,
                        x_cord=float(db_place.x_cord),
                        y_cord=float(db_place.y_cord),
                        category=category,
                        open_time=input_data.start_end.arrivaltime,
                        close_time="",
                        service_time=int(db_place.service_time or 0),
                        tags=getattr(db_place, "tags", []) or [],
                        closed_days=getattr(db_place, "closed_days", []) or [],
                        break_time=getattr(db_place, "break_time", []) or [],
                        is_mandatory=True
                    ))
                    break

        # 2. 일반 장소들
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

        # 3. 출발지 추가 (마지막 날 맨 뒤)
        if date == end_date:
            departure_name = input_data.start_end.departure
            for category, PlaceModel in PLACE_MODELS.items():
                db_place = db.query(PlaceModel).filter(
                    func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(departure_name))
                ).first()
                if db_place:
                    enriched_places.append(PlaceDetailOutput(
                        id=db_place.id,
                        name=db_place.name,
                        x_cord=float(db_place.x_cord),
                        y_cord=float(db_place.y_cord),
                        category=category,
                        open_time="",
                        close_time=input_data.start_end.departuretime,
                        service_time=int(db_place.service_time or 0),
                        tags=getattr(db_place, "tags", []) or [],
                        closed_days=getattr(db_place, "closed_days", []) or [],
                        break_time=getattr(db_place, "break_time", []) or [],
                        is_mandatory=True
                    ))
                    break

        enriched_places_by_day[day_index] = enriched_places

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
    for day_index in sorted(stored_places_by_day.keys()):

        day_places = []

        for place in stored_places_by_day[day_index]:
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
                            service_time=int(place["service_time"] if isinstance(place, dict) and "service_time" in place 
                                             else db_place.service_time or 0),
                            image_urls=image_urls
                        )
                    )
                    break

        result_places_by_day[day_index] = day_places

    return ScheduleShowOutput(
        date=date_info,
        start_end=start_end_info,
        places_by_day=result_places_by_day  
    )

@router.post("/service_time", response_model=EditServiceTimeOutput)
def edit_service_time(input: EditServiceTimeInput):
    user_id = input.user_id
    day = input.day
    place_name = input.place_name.strip()
    new_service_time = input.new_service_time

    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="해당 사용자의 일정이 없습니다.")

    day_places = user_schedules[user_id]["places_by_day"].get(day)
    if not day_places:
        raise HTTPException(status_code=404, detail=f"{day}일차 일정이 존재하지 않습니다.")

    updated_list = []

    for i, place in enumerate(day_places):
        name = place["name"] if isinstance(place, dict) else place.name
        if name == place_name:
            if not isinstance(place, dict):
                place = place.__dict__
                day_places[i] = place  # 객체 → dict 교체

            place["service_time"] = new_service_time

        updated_list.append(
            PlaceWithTime(name=place["name"] if isinstance(place, dict) else place.name,
                          service_time=place.get("service_time", 0) if isinstance(place, dict) else getattr(place, "service_time", 0))
        )

    return EditServiceTimeOutput(places_by_day={day: updated_list})

