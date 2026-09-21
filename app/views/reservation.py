from flask import Blueprint, render_template

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.get("/<int:id>/payment")
def payment(id):
    return render_template("reservation/payment.html")


@reservation_bp.get("/<int:id>/complete")
def complete(id):
    return render_template("reservation/complete.html")