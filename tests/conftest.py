import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from main import app
from app.core.config import settings

# Crear una base de datos SQLite en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """
    Fixture para proporcionar una sesión de base de datos para pruebas
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Crea las tablas en la base de datos de prueba
    Base.metadata.create_all(bind=connection)
    
    yield session
    
    # Rollback de la transacción después de cada prueba
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """
    Fixture para proporcionar un cliente de prueba
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Sobreescribir la dependencia de la base de datos
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restaurar la dependencia original
    app.dependency_overrides = {}

@pytest.fixture
def test_user(db_session):
    """
    Fixture para crear un usuario de prueba
    """
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    
    # Primero consultamos si el usuario ya existe
    existing_user = db_session.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
    
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        name="Test User",
        role=UserRole.ATTENDEE
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield user

@pytest.fixture
def test_organizer(db_session):
    """
    Fixture para crear un organizador de prueba
    """
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    
    # Primero consultamos si el organizador ya existe
    existing_organizer = db_session.query(User).filter(User.email == "organizer@example.com").first()
    if existing_organizer:
        return existing_organizer
    
    organizer = User(
        email="organizer@example.com",
        password_hash=get_password_hash("organizerpass"),
        name="Test Organizer",
        role=UserRole.ORGANIZER
    )
    
    db_session.add(organizer)
    db_session.commit()
    db_session.refresh(organizer)
    
    yield organizer

@pytest.fixture
def test_admin(db_session):
    """
    Fixture para crear un administrador de prueba
    """
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    
    # Primero consultamos si el admin ya existe
    existing_admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if existing_admin:
        return existing_admin
    
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpass"),
        name="Test Admin",
        role=UserRole.ADMIN
    )
    
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    yield admin

@pytest.fixture
def test_event(db_session, test_organizer):
    """
    Fixture para crear un evento de prueba
    """
    from app.models.event import Event, EventStatus
    from datetime import datetime, timedelta
    
    # Primero consultar si el evento ya existe para evitar duplicados
    existing_event = db_session.query(Event).filter(
        Event.name == "Test Event",
        Event.organizer_id == test_organizer.id
    ).first()
    
    if existing_event:
        return existing_event
    
    # Eliminar microsegundos para SQLite
    event_date = (datetime.now() + timedelta(days=7)).replace(microsecond=0)
    
    event = Event(
        name="Test Event",
        description="This is a test event for unit testing with sufficient length to pass validation",
        location="Test Location",
        date=event_date,
        capacity=100,
        registered_attendees=0,
        status=EventStatus.UPCOMING,
        organizer_id=test_organizer.id
    )
    
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    yield event

@pytest.fixture
def test_speaker(db_session):
    """
    Fixture para crear un ponente de prueba
    """
    from app.models.speaker import Speaker
    
    # Primero consultamos si el ponente ya existe
    existing_speaker = db_session.query(Speaker).filter(Speaker.name == "Test Speaker").first()
    if existing_speaker:
        return existing_speaker
    
    speaker = Speaker(
        name="Test Speaker",
        bio="This is a test speaker for unit testing with a sufficiently long bio"
    )
    
    db_session.add(speaker)
    db_session.commit()
    db_session.refresh(speaker)
    
    yield speaker

@pytest.fixture
def test_session(db_session, test_event, test_speaker):
    """
    Fixture para crear una sesión de prueba
    """
    from app.models.session import Session
    from datetime import datetime, timedelta
    
    event_date = test_event.date
    
    # Eliminar microsegundos para SQLite
    start_time = event_date.replace(hour=10, minute=0, microsecond=0)
    end_time = event_date.replace(hour=11, minute=30, microsecond=0)
    
    # Primero consultamos si la sesión ya existe
    existing_session = db_session.query(Session).filter(
        Session.event_id == test_event.id,
        Session.title == "Test Session"
    ).first()
    
    if existing_session:
        return existing_session
    
    session = Session(
        event_id=test_event.id,
        title="Test Session",
        description="This is a test session for unit testing with a sufficiently long description",
        speaker_id=test_speaker.id,
        start_time=start_time,
        end_time=end_time,
        location="Test Room",
        capacity=50,
        registered_attendees=0
    )
    
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    yield session

@pytest.fixture
def test_category(db_session):
    """
    Fixture para crear una categoría de prueba
    """
    from app.models.category import Category
    
    existing_category = db_session.query(Category).filter(Category.name == "Test Category").first()
    if existing_category:
        return existing_category
    
    category = Category(
        name="Test Category",
        description="This is a test category for unit testing",
        color="#3498DB"
    )
    
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    yield category

@pytest.fixture
def token_headers(client, test_user):
    """
    Fixture para generar headers con token de autenticación
    """
    # Generar token de acceso
    login_data = {
        "username": test_user.email,
        "password": "testpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return headers

@pytest.fixture
def organizer_token_headers(client, test_organizer):
    """
    Fixture para generar headers con token de autenticación de organizador
    """
    login_data = {
        "username": test_organizer.email,
        "password": "organizerpass"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return headers

@pytest.fixture
def admin_token_headers(client, test_admin):
    """
    Fixture para generar headers con token de autenticación de administrador
    """
    login_data = {
        "username": test_admin.email,
        "password": "adminpass"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return headers