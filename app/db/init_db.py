import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, Base, engine
from app.core.config import settings
from app.schemas.user import UserCreate
from app.repositories.user_repository import user_repository
from app.models.event import Event, EventStatus
from app.models.user import User

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
    admin = user_repository.get_by_email(db, email="admin@miseventos.com")
    if not admin:
        try:
            user_in = UserCreate(
                email="admin@miseventos.com",
                password="admin123",
                name="Administrator",
                role="ADMIN"
            )
            admin = user_repository.create(db, obj_in=user_in)
            logger.info("Superuser created")
        except Exception as e:
            logger.error(f"Error creating superuser: {e}")
    
    test_user = user_repository.get_by_email(db, email="test@miseventos.com")
    if not test_user:
        try:
            user_in = UserCreate(
                email="test@miseventos.com",
                password="test123",
                name="Test User",
                role="ATTENDEE"
            )
            test_user = user_repository.create(db, obj_in=user_in)
            logger.info("Test user created")
        except Exception as e:
            logger.error(f"Error creating test user: {e}")
    
    organizer = user_repository.get_by_email(db, email="organizer@miseventos.com")
    if not organizer:
        try:
            user_in = UserCreate(
                email="organizer@miseventos.com",
                password="organizer123",
                name="Organizer User",
                role="ORGANIZER"
            )
            organizer = user_repository.create(db, obj_in=user_in)
            logger.info("Organizer user created")
        except Exception as e:
            logger.error(f"Error creating organizer user: {e}")
    
    events_count = db.query(Event).count()
    if events_count == 0 and organizer:
        try:
            create_sample_events(db, organizer)
            logger.info("Sample events created")
        except Exception as e:
            logger.error(f"Error creating sample events: {e}")

def create_sample_events(db: Session, organizer: User) -> None:
    """
    Create sample events
    """
    today = datetime.utcnow()
    
    upcoming_event = Event(
        name="Tech Conference 2025",
        description="The biggest tech conference with the latest trends in AI, Web Development, Mobile and Cloud.",
        location="Convention Center, Santiago",
        date=today + timedelta(days=30),
        end_date=today + timedelta(days=32),
        capacity=500,
        registered_attendees=100,
        status=EventStatus.UPCOMING,
        image_url="https://source.unsplash.com/random/?tech,conference",
        organizer_id=organizer.id
    )
    
    ongoing_event = Event(
        name="Summer Music Festival",
        description="A three-day music festival featuring top artists from around the world.",
        location="Central Park, Santiago",
        date=today - timedelta(days=1),
        end_date=today + timedelta(days=1),
        capacity=1000,
        registered_attendees=900,
        status=EventStatus.ONGOING,
        image_url="https://source.unsplash.com/random/?music,festival",
        organizer_id=organizer.id
    )
    
    completed_event = Event(
        name="Art Exhibition 2024",
        description="An exhibition showcasing works from emerging artists in the contemporary art scene.",
        location="Modern Art Museum, Santiago",
        date=today - timedelta(days=30),
        end_date=today - timedelta(days=15),
        capacity=200,
        registered_attendees=150,
        status=EventStatus.COMPLETED,
        image_url="https://source.unsplash.com/random/?art,exhibition",
        organizer_id=organizer.id
    )
    
    db.add_all([upcoming_event, ongoing_event, completed_event])
    db.commit()

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")