from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.get("/signup")
def signup():
    return render_template("auth/signup.html")


@auth_bp.get("/find-email")
def find_email():
    return render_template("auth/find_email.html")


@auth_bp.get("/reset-password")
def reset_password():
    return render_template("auth/reset_password.html")