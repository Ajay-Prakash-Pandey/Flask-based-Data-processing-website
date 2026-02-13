import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    _db_url = os.getenv("DATABASE_URL", "sqlite:///data.db")
    # Render and some providers may expose postgres:// URLs that SQLAlchemy doesn't accept.
    SQLALCHEMY_DATABASE_URI = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
