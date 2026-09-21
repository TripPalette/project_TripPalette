from flask import Blueprint, render_template

recommendation_bp = Blueprint("recommendation", __name__)


@recommendation_bp.get("/survey")
def survey():
    return render_template("recommendation/survey.html")


@recommendation_bp.get("/result")
def result():
    return render_template("recommendation/result.html")