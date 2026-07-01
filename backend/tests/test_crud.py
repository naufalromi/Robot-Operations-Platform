from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_read_robot():
    response = client.post("/robots", json={
        "name": "TestBot",
        "battery": 100,
        "status": "Idle",
        "x": 0,
        "y": 0,
        "task": "Testing"
    })
    assert response.status_code == 201
    
    robot_id = response.json()["id"]
    
    response = client.get(f"/robots/{robot_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "TestBot"
