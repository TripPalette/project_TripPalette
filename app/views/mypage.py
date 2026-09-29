from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from sqlalchemy.orm import selectinload

from app import db
from app.auth_helpers import login_required
from app.models import Favorite, Review

mypage_bp = Blueprint("mypage", __name__)


@mypage_bp.get("")
@login_required
def index():
    return redirect(url_for("mypage.favorites"))


@mypage_bp.get("/favorites")
@login_required
def favorites():
    user_favorites = list(
        db.session.execute(
            db.select(Favorite)
            .options(selectinload(Favorite.destination))
            .where(Favorite.user_id == g.user.id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).scalars()
    )
    return render_template("mypage/favorites.html", favorites=user_favorites)


@mypage_bp.get("/reservations")
@login_required
def reservations():
    """예약 내역 데이터 연결은 Phase 5에서 구현한다."""
    return render_template("mypage/reservations.html")


@mypage_bp.get("/reviews")
@login_required
def reviews():
    user_reviews = list(
        db.session.execute(
            db.select(Review)
            .options(selectinload(Review.destination))
            .where(Review.user_id == g.user.id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).scalars()
    )
    return render_template("mypage/reviews.html", reviews=user_reviews)


@mypage_bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()

        if not name or not phone:
            flash("이름과 전화번호를 모두 입력해 주세요.", "error")
        else:
            g.user.name = name
            g.user.phone = phone
            db.session.commit()
            flash("회원정보가 수정되었습니다.", "success")
            return redirect(url_for("mypage.profile"))

    return render_template("mypage/profile.html", user=g.user)
