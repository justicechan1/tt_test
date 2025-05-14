#router/maps.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import re
from datetime import datetime
from app.database import get_db
from app.models.jeju_cafe import JejuCafe, JejuCafeHashtag
from app.models.jeju_restaurant import JejuRestaurant, JejurestaurantHashtag
from app.models.jeju_tourism import JejuTourism, JejutourismHashtag
from app.models.jeju_hotel import JejuHotel, JejuhotelHashtag
from app.schemas.maps import (
    HashtagInput, HashtagOutput, TagInfo,
    MoveResponse, MoveInput, MoveInfo, VisitInfo,
    PathPoint, RouteResponse
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
        PlaceModel.x_cord >= viewport.min_x,
        PlaceModel.x_cord <= viewport.max_x,
        PlaceModel.y_cord >= viewport.min_y,
        PlaceModel.y_cord <= viewport.max_y
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
            PlaceModel.x_cord >= viewport.min_x,
            PlaceModel.x_cord <= viewport.max_x,
            PlaceModel.y_cord >= viewport.min_y,
            PlaceModel.y_cord <= viewport.max_y
        ).subquery()

        tagged_ids = db.query(fk_field).filter(
            fk_field.in_(subquery),
            HashtagModel.hashtag_name != None
        ).all()

        id_list = [r[0] for r in tagged_ids]

        for place_id in id_list:
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

            place = db.query(PlaceModel).filter(
                pk_field == place_id
            ).first()

            if place:
                results.append(MoveInfo(
                    name=place.name,
                    x_cord=float(place.x_cord),
                    y_cord=float(place.y_cord)
                ))

    return MoveResponse(move=results)

def convert_to_move_response(data: dict) -> RouteResponse:
    visits = [
        VisitInfo(
            order=v["order"],
            place=v["place"],
            arrival_str=v["arrival_str"],
            departure_str=v["departure_str"],
            stay_duration=v["stay_duration"],
            x_cord=v["x_cord"],
            y_cord=v["y_cord"],
            travel_time=v.get("travel_time"),
            wait_time=v.get("wait_time")
        )
        for v in data.get("visits", [])
    ]

    path = [
        [[p[0], p[1]] for p in segment]
        for segment in data.get("path", [])
    ]

    return RouteResponse(visits=visits, path=path)

@router.post("/route", response_model=RouteResponse)
def get_optimal_route(input_data: dict):
    result = schedule_trip(input_data)
    return convert_to_move_response(result)
