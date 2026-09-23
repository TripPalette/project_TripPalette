from flask import Blueprint, render_template

from app import db
from app.models import Destination


main_bp = Blueprint("main", __name__)

POPULAR_DESTINATION_NAMES = ("제주", "부산", "경주", "강릉")
HERO_SLIDES = (
    {
        "filename": "img/main/hero-jeju-sunset.png",
        "alt": "제주 바다와 야자수가 어우러진 노을 풍경",
    },
    {
        "filename": "img/main/hero-busan-gwangalli-hd.png",
        "alt": "부산 광안리 바다를 지나는 요트와 해안 도시 풍경",
    },
    {
        "filename": "img/main/hero-pohang-sunset-hd.png",
        "alt": "붉은 노을 아래 포항 호미곶 상생의 손",
    },
    {
        "filename": "img/main/hero-geochang-hd.png",
        "alt": "산과 구름을 내려다보는 거창의 전망대",
    },
)


@main_bp.get("/")
def index():
    """정적 히어로 자산과 DB 인기 여행지로 메인을 구성한다."""
    popular_rows = db.session.execute(
        db.select(Destination).where(
            Destination.name.in_(POPULAR_DESTINATION_NAMES)
        )
    ).scalars()
    destinations_by_name = {
        destination.name: destination for destination in popular_rows
    }
    popular_destinations = [
        destinations_by_name[name]
        for name in POPULAR_DESTINATION_NAMES
        if name in destinations_by_name
    ]

    return render_template(
        "main/index.html",
        hero_slides=HERO_SLIDES,
        popular_destinations=popular_destinations,
    )
