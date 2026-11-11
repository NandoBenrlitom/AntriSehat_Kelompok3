import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# Menggunakan SQLite in-memory agar pengujian terisolasi dan tidak bergantung pada container DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_appointment_quota_limit():
    # Menembak endpoint 30 kali untuk mengisi kuota
    for _ in range(30):
        res = client.post("/appointments?poli=Gigi")
        assert res.status_code == 200

    # Request ke-31 harus ditolak (HTTP 400)
    response = client.post("/appointments?poli=Gigi")
    assert response.status_code == 400
    assert "Kuota dokter penuh" in response.json()["detail"]

def test_get_queue_number():
    res1 = client.post("/queues?poli=Umum")
    assert res1.status_code == 200
    assert res1.json()["nomor_antrean"] == 1

    res2 = client.post("/queues?poli=Umum")
    assert res2.status_code == 200
    assert res2.json()["nomor_antrean"] == 2
