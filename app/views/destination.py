from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app import db
from app.models import Accommodation, Destination, Review


destination_bp = Blueprint("destination", __name__)

FILTER_COLUMNS = {
    "region": Destination.region,
    "season": Destination.season,
    "purpose": Destination.purpose,
    "atmosphere": Destination.atmosphere,
}


def _distinct_values(column):
    """필터 Select에 표시할 빈 값 없는 고유 목록을 반환한다."""
    statement = (
        db.select(column)
        .where(column.is_not(None), column != "")
        .distinct()
        .order_by(column)
    )
    return list(db.session.execute(statement).scalars())


@destination_bp.get("", endpoint="list")
def destination_list():
    keyword = request.args.get("keyword", "").strip()
    selected_filters = {
        name: request.args.get(name, "").strip() for name in FILTER_COLUMNS
    }

    statement = db.select(Destination)
    if keyword:
        search_pattern = f"%{keyword}%"
        statement = statement.where(
            or_(
                Destination.name.ilike(search_pattern),
                Destination.region.ilike(search_pattern),
                Destination.description.ilike(search_pattern),
            )
        )

    for name, column in FILTER_COLUMNS.items():
        selected_value = selected_filters[name]
        if selected_value:
            statement = statement.where(column == selected_value)

    destinations = list(
        db.session.execute(statement.order_by(Destination.id)).scalars()
    )
    filters = {
        "regions": _distinct_values(Destination.region),
        "seasons": _distinct_values(Destination.season),
        "purposes": _distinct_values(Destination.purpose),
        "atmospheres": _distinct_values(Destination.atmosphere),
    }

    return render_template(
        "destination/list.html",
        destinations=destinations,
        filters=filters,
        selected_filters=selected_filters,
        keyword=keyword,
    )


@destination_bp.get("/<int:id>")
def detail(id):
    destination = db.get_or_404(Destination, id)
    reviews = list(
        db.session.execute(
            db.select(Review)
            .where(Review.destination_id == destination.id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).scalars()
    )
    accommodations = list(
        db.session.execute(
            db.select(Accommodation)
            .where(Accommodation.destination_id == destination.id)
            .order_by(Accommodation.id)
            .limit(3)
        ).scalars()
    )

    return render_template(
        "destination/detail.html",
        destination=destination,
        reviews=reviews,
        accommodations=accommodations,
    )


@destination_bp.get("/<int:id>/accommodations")
def accommodations(id):
    destination = db.get_or_404(Destination, id)
    nearby_accommodations = list(
        db.session.execute(
            db.select(Accommodation)
            .where(Accommodation.destination_id == destination.id)
            .order_by(Accommodation.id)
        ).scalars()
    )

    return render_template(
        "accommodation/list.html",
        destination=destination,
        accommodations=nearby_accommodations,
    )
