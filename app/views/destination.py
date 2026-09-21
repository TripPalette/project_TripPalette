from flask import Blueprint, render_template

destination_bp = Blueprint("destination", __name__)


@destination_bp.get("")
def list():
    return render_template("destination/list.html")


@destination_bp.get("/<int:id>")
def detail(id):
    return render_template("destination/detail.html")
