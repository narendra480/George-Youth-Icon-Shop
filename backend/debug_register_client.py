import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

payload = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser-unique-client@example.com",
    "phone": "1234567890",
    "password": "Abc12345!",
    "confirm_password": "Abc12345!",
}

response = client.post("/api/v1/auth/register", json=payload)
print("STATUS", response.status_code)
print(response.headers)
print(response.text)
if response.status_code >= 400:
    try:
        print(response.json())
    except Exception as exc:
        print("JSON parse error:", exc)
