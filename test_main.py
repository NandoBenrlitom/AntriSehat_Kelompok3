from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

# Simulasi test kuota berlebih (QA akan mengembangkan ini dengan database testing)
def test_appointment_quota_limit():
    # Menembak endpoint 31 kali untuk memastikan request ke-31 ditolak (HTTP 400)
    for _ in range(30):
        client.post("/appointments?poli=Gigi")
        
    response = client.post("/appointments?poli=Gigi")
    assert response.status_code == 400