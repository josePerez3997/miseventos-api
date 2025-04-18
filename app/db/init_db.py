import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session as SQLAlchemySession

from app.db.session import SessionLocal, Base, engine
from app.core.config import settings
from app.schemas.user import UserCreate
from app.repositories.user_repository import user_repository
from app.models.event import Event, EventStatus
from app.models.user import User, UserRole
from app.models.speaker import Speaker
from app.models.session import Session as EventSession

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
        try:
            create_initial_data(db)
        except Exception as e:
            db.rollback() 
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def create_initial_data(db: SQLAlchemySession) -> None:
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
                role=UserRole.ADMIN
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
                role=UserRole.ATTENDEE
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
                role=UserRole.ORGANIZER
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
    
    speakers_count = db.query(Speaker).count()
    if speakers_count == 0:
        try:
            create_sample_speakers(db)
            logger.info("Sample speakers created")
        except Exception as e:
            logger.error(f"Error creating sample speakers: {e}")
    
    from app.models.session import Session as EventSession
    sessions_count = db.query(EventSession).count()
    if sessions_count == 0 and events_count > 0 and speakers_count > 0:
        try:
            create_sample_sessions(db)
            logger.info("Sample sessions created")
        except Exception as e:
            logger.error(f"Error creating sample sessions: {e}")

def create_sample_events(db: SQLAlchemySession, organizer: User) -> None:
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

def create_sample_speakers(db: SQLAlchemySession) -> None:
    """
    Create sample speakers
    """
    speakers = [
        Speaker(
            name="John Smith",
            bio="John is a technology leader with over 15 years experience in AI and machine learning.",
            image_url="https://source.unsplash.com/random/?portrait,man,professional"
        ),
        Speaker(
            name="Sarah Johnson",
            bio="Sarah is the CTO of TechInnovate and specializes in cloud architecture.",
            image_url="https://source.unsplash.com/random/?portrait,woman,professional"
        ),
        Speaker(
            name="Michael Wong",
            bio="Michael is a UI/UX expert and has worked with major tech companies.",
            image_url="https://source.unsplash.com/random/?portrait,asian,man"
        ),
        Speaker(
            name="Emily Chen",
            bio="Emily is a cybersecurity specialist with experience in financial institutions.",
            image_url="https://source.unsplash.com/random/?portrait,asian,woman"
        ),
        Speaker(
            name="David Martinez",
            bio="David is a full-stack developer and open source contributor.",
            image_url="https://source.unsplash.com/random/?portrait,latino,man"
        )
    ]
    
    db.add_all(speakers)
    db.commit()

def create_sample_sessions(db: SQLAlchemySession) -> None:
    """
    Create sample sessions for the first event
    """
    event = db.query(Event).first()
    if not event:
        return
    
    speakers = db.query(Speaker).all()
    if not speakers or len(speakers) < 3:
        return
    
    today = datetime.utcnow()
    event_date = event.date
    
    from app.models.session import Session as EventSession
    
    sessions = [
        EventSession(
            event_id=event.id,
            title="Introducción a la IA",
            description="Una introducción a los conceptos básicos de la Inteligencia Artificial y su aplicación en la industria actual.",
            speaker_id=speakers[0].id,
            start_time=event_date.replace(hour=10, minute=0),
            end_time=event_date.replace(hour=11, minute=30),
            location="Sala Principal",
            capacity=100,
            registered_attendees=0
        ),
        EventSession(
            event_id=event.id,
            title="Desarrollo Web Moderno",
            description="Aprende las últimas tendencias en desarrollo web con React, Angular y Vue.",
            speaker_id=speakers[1].id,
            start_time=event_date.replace(hour=12, minute=0),
            end_time=event_date.replace(hour=13, minute=30),
            location="Sala A",
            capacity=50,
            registered_attendees=0
        ),
        EventSession(
            event_id=event.id,
            title="Seguridad en la Nube",
            description="Estrategias para asegurar aplicaciones y datos en entornos cloud.",
            speaker_id=speakers[2].id,
            start_time=event_date.replace(hour=14, minute=0),
            end_time=event_date.replace(hour=15, minute=30),
            location="Sala B",
            capacity=50,
            registered_attendees=0
        )
    ]
    
    db.add_all(sessions)
    db.commit()

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data created")