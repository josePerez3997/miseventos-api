from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from app.core.config import settings

db_user = settings.POSTGRES_USER
db_password = settings.POSTGRES_PASSWORD
db_host = settings.POSTGRES_SERVER
db_port = settings.POSTGRES_PORT
db_name = settings.POSTGRES_DB

SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URI)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "options": "-c client_encoding=utf8",
        "client_encoding": "utf8"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()