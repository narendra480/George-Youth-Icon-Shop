import json
import urllib.request
import urllib.error

payload = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser-unique-8000@example.com",
    "phone": "1234567890",
    "password": "Abc12345!",
    "confirm_password": "Abc12345!",
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/auth/register",
    data=data,
    headers={"Content-Type": "application/json"},
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print("STATUS", resp.status)
    print(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTPERROR", e.code)
    print(e.read().decode("utf-8"))
except Exception as exc:
    print("EXC", exc)
