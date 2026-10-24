import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.models import (
    User,
    BodyProfile,
    Brand,
    Garment,
    GarmentSize,
    GarmentMeasurement,
    Purchase,
)
from backend.app.core.security import get_password_hash

# In-memory SQLite engine for fast, isolated, deterministic automated testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

from sqlalchemy import event


@event.listens_for(test_engine, "connect")
def register_sqlite_functions(dbapi_connection, connection_record):
    """Registers MySQL functions such as CHAR_LENGTH into SQLite test runtime."""
    dbapi_connection.create_function("CHAR_LENGTH", 1, lambda s: len(s) if s is not None else 0)



@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes tables in the SQLite test database once per session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional database session pre-populated with deterministic Member A test fixtures."""
    db = TestingSessionLocal()
    # Clean tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

    # Seed deterministic test fixtures
    # 1. Users
    user1 = User(user_id=1, name="Admin User", email="admin@fitcheck.local", password_hash=get_password_hash("password123"), role="ADMIN")
    user2 = User(user_id=2, name="Priya Sharma", email="priya@example.com", password_hash=get_password_hash("password123"), role="USER")
    user3 = User(user_id=3, name="Ananya Rao", email="ananya@example.com", password_hash=get_password_hash("password123"), role="USER")
    user4 = User(user_id=4, name="New User", email="newuser@example.com", password_hash=get_password_hash("password123"), role="USER")
    db.add_all([user1, user2, user3, user4])
    db.commit()

    # 2. Body Profiles
    prof2 = BodyProfile(profile_id=1, user_id=2, height=162.0, waist=68.0, hip=94.0, thigh=54.0, inseam=76.0, preferred_fit="REGULAR")
    prof3 = BodyProfile(profile_id=2, user_id=3, height=158.0, waist=64.0, hip=90.0, thigh=51.0, inseam=74.0, preferred_fit="TIGHT")
    db.add_all([prof2, prof3])
    db.commit()

    # 3. Brands
    brand1 = Brand(brand_id=1, brand_name="Levis", sizing_system="WAIST_BASED")
    brand2 = Brand(brand_id=2, brand_name="Zara", sizing_system="NUMERIC")
    brand3 = Brand(brand_id=3, brand_name="H&M", sizing_system="ALPHA")
    db.add_all([brand1, brand2, brand3])
    db.commit()

    # 4. Garments
    g1 = Garment(garment_id=1, brand_id=1, garment_name="Levis 501 Original", garment_category="Jeans", fit_type="STRAIGHT", description="Classic straight")
    g2 = Garment(garment_id=2, brand_id=2, garment_name="Zara Z1975 Wide Leg", garment_category="Jeans", fit_type="WIDE_LEG", description="Wide leg high waist")
    g3 = Garment(garment_id=3, brand_id=3, garment_name="H&M Slim Fit Chinos", garment_category="Trousers", fit_type="SLIM", description="Slim cotton chinos")
    db.add_all([g1, g2, g3])
    db.commit()

    # 5. Garment Sizes
    # Levis sizes 26, 27, 28, 29, 30 (IDs 1-5)
    s1 = GarmentSize(garment_size_id=1, garment_id=1, size_label="26")
    s2 = GarmentSize(garment_size_id=2, garment_id=1, size_label="27")
    s3 = GarmentSize(garment_size_id=3, garment_id=1, size_label="28")
    s4 = GarmentSize(garment_size_id=4, garment_id=1, size_label="29")
    s5 = GarmentSize(garment_size_id=5, garment_id=1, size_label="30")
    # Zara sizes 34, 36, 38, 40 (IDs 6-9)
    s6 = GarmentSize(garment_size_id=6, garment_id=2, size_label="34")
    s7 = GarmentSize(garment_size_id=7, garment_id=2, size_label="36")
    s8 = GarmentSize(garment_size_id=8, garment_id=2, size_label="38")
    s9 = GarmentSize(garment_size_id=9, garment_id=2, size_label="40")
    db.add_all([s1, s2, s3, s4, s5, s6, s7, s8, s9])
    db.commit()

    # 6. Garment Measurements
    measurements = [
        # Levis 28 (ID 3): waist 71cm, hip 96cm
        GarmentMeasurement(measurement_id=1, garment_size_id=3, measurement_type="waist", measurement_value=71.0, unit="cm"),
        GarmentMeasurement(measurement_id=2, garment_size_id=3, measurement_type="hip", measurement_value=96.0, unit="cm"),
        # Levis 26 (ID 1): waist 66cm, hip 91cm
        GarmentMeasurement(measurement_id=3, garment_size_id=1, measurement_type="waist", measurement_value=66.0, unit="cm"),
        GarmentMeasurement(measurement_id=4, garment_size_id=1, measurement_type="hip", measurement_value=91.0, unit="cm"),
        # Zara 36 (ID 7): waist 66cm, hip 94cm
        GarmentMeasurement(measurement_id=5, garment_size_id=7, measurement_type="waist", measurement_value=66.0, unit="cm"),
        GarmentMeasurement(measurement_id=6, garment_size_id=7, measurement_type="hip", measurement_value=94.0, unit="cm"),
        # Zara 38 (ID 8): waist 70cm, hip 98cm
        GarmentMeasurement(measurement_id=7, garment_size_id=8, measurement_type="waist", measurement_value=70.0, unit="cm"),
        GarmentMeasurement(measurement_id=8, garment_size_id=8, measurement_type="hip", measurement_value=98.0, unit="cm"),
        # Zara 40 (ID 9): waist 74cm, hip 102cm
        GarmentMeasurement(measurement_id=9, garment_size_id=9, measurement_type="waist", measurement_value=74.0, unit="cm"),
        GarmentMeasurement(measurement_id=10, garment_size_id=9, measurement_type="hip", measurement_value=102.0, unit="cm"),
    ]
    db.add_all(measurements)
    db.commit()

    # 7. Purchases
    # Priya (user 2): kept Levis sz 28 with GOOD fit
    p1 = Purchase(purchase_id=1, user_id=2, garment_size_id=3, purchase_date=date(2026, 3, 15), outcome="KEPT", fit_satisfaction="GOOD", fit_preference="REGULAR")
    db.add(p1)
    db.commit()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency pointing to the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
