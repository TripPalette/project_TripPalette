import json
from pathlib import Path

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

DESTINATIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "destinations.json"
POPULAR_DESTINATION_NAMES = ("제주", "부산", "경주", "강릉")


def _load_destinations():
    """메인 화면 미리보기에 사용할 개발용 여행지 데이터를 읽는다."""
    try:
        with DESTINATIONS_PATH.open(encoding="utf-8") as file:
            destinations = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    for destination_id, destination in enumerate(destinations, start=1):
        destination["id"] = destination_id
        image_url = destination.get("image_url")
        if image_url and image_url.startswith("http://tong.visitkorea.or.kr/"):
            destination["image_url"] = image_url.replace("http://", "https://", 1)
    return destinations


@main_bp.get("/")
def index():
    destinations = _load_destinations()
    destinations_by_name = {
        destination["name"]: destination for destination in destinations
    }
    popular_destinations = [
        destinations_by_name[name]
        for name in POPULAR_DESTINATION_NAMES
        if name in destinations_by_name
    ]
    hero_destination = destinations_by_name.get("정선")
    if hero_destination is None and destinations:
        hero_destination = destinations[0]

    return render_template(
        "main/index.html",
        hero_destination=hero_destination,
        popular_destinations=popular_destinations,
    )
