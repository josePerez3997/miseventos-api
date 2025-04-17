import logging

from sqlalchemy.orm import Session

from app.db.session import engine, Base, SessionLocal
from app.models import User  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize database tables and create initial data if needed
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        db = SessionLocal()
        create_initial_data(db)
        db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def create_initial_data(db: Session) -> None:
    """
    Create initial data in the database
    """
    pass

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")