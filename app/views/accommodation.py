from flask import Blueprint, render_template

accommodation_bp = Blueprint("accommodation", __name__)


@accommodation_bp.get("")
def list():
    return render_template("accommodation/list.html")


@accommodation_bp.get("/<int:id>")
def detail(id):
    return render_template("accommodation/detail.html")
