from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.views.main import main_bp

    app.register_blueprint(main_bp)

    return app

@app.route('/hyh')
def hyh():
    return render_template(hyh.html)

   return app
