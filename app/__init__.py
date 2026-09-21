from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # 기존 설정 유지
    app.config.from_object("config")

    # 기존 확장 기능 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint import
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.destination import destination_bp
    from app.views.accommodation import accommodation_bp
    from app.views.recommendation import recommendation_bp
    from app.views.reservation import reservation_bp
    from app.views.mypage import mypage_bp



    # Blueprint 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(destination_bp, url_prefix="/destinations")
    app.register_blueprint(accommodation_bp, url_prefix="/accommodations")
    app.register_blueprint(recommendation_bp, url_prefix="/recommend")
    app.register_blueprint(reservation_bp, url_prefix="/reservations")
    app.register_blueprint(mypage_bp, url_prefix="/mypage")


    return app