import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
    UNSPLASH_APP_NAME = os.environ.get("UNSPLASH_APP_NAME", "trippalette")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
