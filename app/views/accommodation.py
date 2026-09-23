from flask import Blueprint, render_template

from app import db
from app.models import Accommodation


accommodation_bp = Blueprint("accommodation", __name__)


@accommodation_bp.get("", endpoint="list")
def accommodation_list():
    accommodations = list(
        db.session.execute(
            db.select(Accommodation).order_by(Accommodation.id)
        ).scalars()
    )
    return render_template(
        "accommodation/list.html",
        destination=None,
        accommodations=accommodations,
    )


@accommodation_bp.get("/<int:id>")
def detail(id):
    accommodation = db.get_or_404(Accommodation, id)
    return render_template(
        "accommodation/detail.html",
        accommodation=accommodation,
    )
