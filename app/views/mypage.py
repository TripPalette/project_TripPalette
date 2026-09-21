from flask import Blueprint, render_template

mypage_bp = Blueprint("mypage", __name__)


@mypage_bp.get("")
def mypage():
    return render_template("mypage/index.html")


@mypage_bp.get("/favorites")
def favorites():
    return render_template("mypage/favorites.html")


@mypage_bp.get("/reservations")
def reservations():
    return render_template("mypage/reservations.html")


@mypage_bp.get("/reviews")
def reviews():
    return render_template("mypage/reviews.html")


@mypage_bp.get("/profile")
def profile():
    return render_template("mypage/profile.html")