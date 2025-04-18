import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, Base, engine
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.repositories.user_repository import user_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize database by creating tables and adding initial data
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
    user = user_repository.get_by_email(db, email="admin@miseventos.com")
    if not user:
        user_in = UserCreate(
            email="admin@miseventos.com",
            password="admin123",
            name="Administrator",
            role=UserRole.ADMIN
        )
        user = user_repository.create(db, obj_in=user_in)
        logger.info("Superuser created")

    test_user = user_repository.get_by_email(db, email="test@miseventos.com")
    if not test_user:
        user_in = UserCreate(
            email="test@miseventos.com",
            password="test123",
            name="Test User",
            role=UserRole.ATTENDEE
        )
        test_user = user_repository.create(db, obj_in=user_in)
        logger.info("Test user created")

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")