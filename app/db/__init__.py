from app.db.session import Base, engine, get_db, SessionLocal
from app.db.base_class import CustomBase

def create_tables():
    Base.metadata.create_all(bind=engine)