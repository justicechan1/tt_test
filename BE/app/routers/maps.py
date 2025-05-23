# router/maps.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import re
from datetime import datetime
from typing import List
from app.cache import user_schedules, selected_category_cache
from app.database import get_db
import json 
import numpy as np
from app.models.jeju_cafe import JejuCafe, JejuCafeHashtag
from app.models.jeju_restaurant import JejuRestaurant, JejurestaurantHashtag
from app.models.jeju_tourism import JejuTourism, JejutourismHashtag
from app.models.jeju_hotel import JejuHotel, JejuhotelHashtag
from app.models.jeju_transport import JejuTransport
from app.schemas.maps import (
    HashtagInput, HashtagOutput, TagInfo,
    MoveInput, MoveResponse, MoveInfo,
    RouteInput, RouteResponse, VisitInfo,
    Viewport
)
from app.core.search import search_similar_places
from TripScheduler.tripscheduler.scheduler_api import schedule_trip

router = APIRouter(prefix="/api/users/maps", tags=["maps"])

PLACE_MODELS = {
    "cafe": (JejuCafe, JejuCafeHashtag),
    "restaurant": (JejuRestaurant, JejurestaurantHashtag),
    "tourism": (JejuTourism, JejutourismHashtag),
    "hotel": (JejuHotel, JejuhotelHashtag),
    "transport": (JejuTransport, None)
}

PRIMARY_KEY_FIELDS = {
    "cafe": "cafe_id",
    "restaurant": "restaurant_id",
    "tourism": "tour_id",
    "hotel": "hotel_id"
}

@router.post("/hashtage", response_model=HashtagOutput)
def get_hashtags(input_data: HashtagInput, db: Session = Depends(get_db)):
    category = input_data.category.lower()
    viewport = input_data.viewport

    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")

    # ✅ 카테고리 캐시 저장 (단일 사용자 가정)
    selected_category_cache["current"] = category

    PlaceModel, HashtagModel = PLACE_MODELS[category]
    pk_field = getattr(PlaceModel, PRIMARY_KEY_FIELDS[category])
    fk_field = getattr(HashtagModel, PRIMARY_KEY_FIELDS[category])

    subquery = db.query(pk_field).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).subquery()

    hashtag_rows = db.query(HashtagModel.hashtage_name).filter(
        fk_field.in_(subquery),
        HashtagModel.hashtage_name.isnot(None)
    ).all()

    unique_tags = set()
    for row in hashtag_rows:
        if not row.hashtage_name:
            continue
        try:
            tags = re.findall(r'#\w+', row.hashtage_name)
            unique_tags.update(tags)
        except Exception as e:
            print(f"❌ 해시태그 파싱 실패: {e}")

    print(f"✅ 최종 해시태그 목록: {list(unique_tags)}")
    return HashtagOutput(tag=[TagInfo(hashtage_name=tag) for tag in unique_tags])

def get_places_in_viewport(category: str, viewport: Viewport, db: Session) -> List[MoveInfo]:
    if category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="Invalid category")

    PlaceModel, _ = PLACE_MODELS[category]

    places = db.query(PlaceModel).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).all()

    results = []
    for place in places:
        print(f"📍 선택된 장소: {place.name} ({place.x_cord}, {place.y_cord})")
        results.append(MoveInfo(
            name=place.name,
            x_cord=float(place.x_cord),
            y_cord=float(place.y_cord)
        ))

    return results
def collect_place_embeddings(db, PlaceModel, HashtagModel, pk_field_name, viewport):
    places = db.query(PlaceModel).filter(
        PlaceModel.x_cord.between(viewport.min_x, viewport.max_x),
        PlaceModel.y_cord.between(viewport.min_y, viewport.max_y)
    ).all()

    embedding_logs = []
    for place in places:
        place_id = getattr(place, pk_field_name)
        if HashtagModel:
            rows = db.query(HashtagModel.embeddings).filter(
                getattr(HashtagModel, pk_field_name) == place_id,
                HashtagModel.embeddings.isnot(None)
            ).all()
            emb_list = [np.array(e[0], dtype=np.float32).reshape(1, -1) for e in rows if e[0] is not None]
            if emb_list:
                embedding_logs.append({
                    "id": place_id,
                    "embedding": np.vstack(emb_list)
                })
    return embedding_logs

def collect_selected_embeddings(db, HashtagModel, tags, seen_embeddings: set):
    selected = []
    for tag in tags:
        rows = db.query(HashtagModel.hashtage_name, HashtagModel.embeddings).filter(
            HashtagModel.hashtage_name.like(f"%{tag}%")
        ).all()
        for name, embedding in rows:
            if embedding is None:
                continue
            key = str(embedding)
            if key in seen_embeddings:
                continue
            seen_embeddings.add(key)
            selected.append(np.array(embedding, dtype=np.float32).reshape(1, -1))
    return selected

def get_top_place_ids(selected_embeddings, embedding_logs):
    top_ids = set()
    for query_vector in selected_embeddings:
        top_results = search_similar_places(query_vector.T, embedding_logs, top_k=5)
        for res in top_results:
            top_ids.add(res["place_id"])
    return top_ids

def build_filtered_move_response(db, PlaceModel, pk_field_name, place_ids):
    move_infos = []
    for pid in place_ids:
        db_place = db.query(PlaceModel).filter(getattr(PlaceModel, pk_field_name) == pid).first()
        if db_place:
            move_infos.append(MoveInfo(
                name=db_place.name,
                x_cord=float(db_place.x_cord),
                y_cord=float(db_place.y_cord)
            ))
    return move_infos

@router.post("/move", response_model=MoveResponse)
def get_move_candidates(input_data: MoveInput, db: Session = Depends(get_db)):
    viewport = input_data.viewport
    tags = [t.hashtage_name for t in input_data.tag]

    category = selected_category_cache.get("current")
    if not category or category not in PLACE_MODELS:
        raise HTTPException(status_code=400, detail="No category selected or invalid")

    PlaceModel, HashtagModel = PLACE_MODELS[category]
    pk_field_name = PRIMARY_KEY_FIELDS[category]

    embedding_logs = collect_place_embeddings(db, PlaceModel, HashtagModel, pk_field_name, viewport)
    selected_embeddings = collect_selected_embeddings(db, HashtagModel, tags, seen_embeddings=set())
    top_place_ids = get_top_place_ids(selected_embeddings, embedding_logs)
    filtered_places = build_filtered_move_response(db, PlaceModel, pk_field_name, top_place_ids)

    return MoveResponse(move=filtered_places)


# ---------- 경로 결과 포맷 변환 ----------
def is_same_coord(p1, p2, tol=1e-6):
    return abs(p1[0] - p2[0]) < tol and abs(p1[1] - p2[1]) < tol

def convert_to_move_response(data: dict) -> RouteResponse:
    visits = [VisitInfo(**v) for v in data.get("visits", [])]
    path = data.get("path", [])

    def is_same_coord(p1, p2, tol=1e-6):
        return abs(p1[0] - p2[0]) < tol and abs(p1[1] - p2[1]) < tol

    # 시작점과 마지막 segment의 도착지가 같으면 제거
    if len(path) >= 2:
        first = path[0][0]
        last = path[-1][1]
        if is_same_coord(first, last):
            path = path[:-1]  # 마지막 segment 제거

    formatted_path = [[[p[0], p[1]] for p in segment] for segment in path]
    return RouteResponse(visits=visits, path=formatted_path)


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

# 카테고리 키워드 매핑
CATEGORY_KEYWORD_MAPPING = {
    "accommodation": [
        "숙박", "호텔", "모텔", "리조트", "리조트부속건물", "펜션", "펜션부속시설",
        "게스트하우스", "민박", "전통숙소", "생활형숙박시설", "쉐어하우스", "레지던스",
        "여관", "원룸"
        ],
    "restaurant": [
        "음식점", "가정식", "갈비탕", "감자탕", "게요리", "고기요리", "곰탕", "곱창", "국밥", "국수",
        "김밥", "꼬치", "낙지요리", "닭갈비", "닭강정", "닭발", "닭볶음탕", "닭요리", "덮밥", "도넛",
        "도시락", "돈가스", "돼지고기구이", "두부요리", "라면", "마라탕", "막국수", "만두", "매운탕",
        "백숙", "보리밥", "보쌈", "복어요리", "분식", "불닭", "뷔페", "브런치", "브런치카페", "비빔밥",
        "생선구이", "생선요리", "생선회", "샌드위치", "샐러드", "샐러드뷔페", "샤브샤브", "소고기구이",
        "소바", "순대", "술집", "스테이크", "스파게티", "아귀찜", "아이스크림", "양갈비", "양꼬치",
        "양식", "오니기리", "오리요리", "오징어요리", "요리주점", "이자카야", "이탈리아음식", "일식당",
        "일품순두부", "전", "전골", "전복요리", "주꾸미요리", "죽", "중식당", "중식만두", "찐빵", "찜닭",
        "케이크전문", "토스트", "포장마차", "푸드코트", "푸드트럭", "퓨전음식", "핫도그", "해장국",
        "햄버거", "향토음식", "호떡"
        ],
    "landmark": [
        "산", "계곡", "해변", "폭포", "섬", "호수", "동굴", "숲", "평야", "저수지",
        "자연", "자연명소", "자연공원", "봉우리", "명소", "유적", "유적지", "사찰",
        "성곽명", "기념관", "기념물", "문화", "문화시설", "문화원", "박물관", "미술관",
        "기념품", "전시관", "홍보관", "체험", "체험여행", "체험마을", "관광농원",
        "관광안내소", "관광민예품", "관광선", "유원지", "테마공원", "테마파크", "놀이기구",
        "워터파크", "눈썰매장", "레일바이크", "ATV체험장", "승마장", "스킨스쿠버", "서핑",
        "실내놀이터", "실내서핑", "캠핑", "해양레저", "항공레저", "짚라인", "드라이브",
        "레저", "레포츠시설", "요트", "잠수함", "배낚시", "전망대", "일출명소", "등산코스",
        "산책로", "수목원", "근린공원", "공원", "등대", "오름", "항구", "선착장",
        "도보코스", "명상", "템플스테이"
        ],
    "transport": ["transport"]
}

def map_category_by_keywords(raw_category: str, default_category: str) -> str:
    if not raw_category:
        return default_category

    lower_category = raw_category.lower()
    for mapped_category, keywords in CATEGORY_KEYWORD_MAPPING.items():
        if any(keyword in lower_category for keyword in keywords):
            return mapped_category
    return default_category

# ---------- route 입력을 위한 dict 구성 ----------
def build_schedule_input(user_id: str, target_date: str, db: Session) -> dict:
    if user_id not in user_schedules:
        raise HTTPException(status_code=404, detail="사용자 일정이 존재하지 않습니다.")

    schedule_data = user_schedules[user_id]
    places_by_day = schedule_data["places_by_day"]
    user_info = schedule_data["user"]

    # 해당 날짜의 장소가 없거나 비어 있으면 빈 리스트 반환
    if target_date not in places_by_day or not places_by_day[target_date]:
        return {
            "places": [],
            "user": user_info.dict(),
            "day_info": get_day_info(user_id, target_date)
        }

    place_objs: List[dict] = []
    for place in places_by_day[target_date]:
        place_name = place["name"] if isinstance(place, dict) else place.name

        for category, (PlaceModel, _) in PLACE_MODELS.items():
            db_place = db.query(PlaceModel).filter(
                func.trim(func.lower(PlaceModel.name)) == func.trim(func.lower(place_name))
            ).first()
            if db_place:
                original_category = category
                mapped_category = map_category_by_keywords(db_place.category, original_category)

                place_objs.append({
                    "id": db_place.id,
                    "name": db_place.name,
                    "x_cord": float(db_place.x_cord),
                    "y_cord": float(db_place.y_cord),
                    "category": mapped_category,
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
    input_dict = build_schedule_input(
        user_id=input_data.user_id,
        target_date=input_data.date,
        db=db
    )

    # 장소가 하나도 없는 경우 빈 결과 반환
    if not input_dict["places"]:
        return RouteResponse(visits=[], path=[])

    # 경로 최적화 실행
    result = schedule_trip(input_dict)

    if not result.get("visits"):
        print("⚠️ 경로 최적화 실패: 기존 일정 유지")
        return RouteResponse(visits=[], path=[])

    # 최적화 성공한 경우에만 places_by_day 갱신
    ordered_place_names = [visit["place"] for visit in result["visits"]]
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