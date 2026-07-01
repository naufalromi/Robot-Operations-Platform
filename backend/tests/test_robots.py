def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_robot(client):
    robot_data = {
        "name": "TestBot",
        "battery": 100,
        "status": "idle",
        "x": 0,
        "y": 0,
    }
    response = client.post("/robots", json=robot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "TestBot"
    assert data["battery"] == 100
    assert data["status"] == "idle"
    assert data["x"] == 0
    assert data["y"] == 0
    assert "id" in data
    assert "last_heartbeat" in data


def test_create_robot_with_task(client):
    robot_data = {
        "name": "TaskBot",
        "battery": 80,
        "status": "moving",
        "x": 5,
        "y": 10,
        "task": "patrol",
    }
    response = client.post("/robots", json=robot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["task"] == "patrol"


def test_get_robots(client):
    client.post("/robots", json={
        "name": "Bot1", "battery": 90, "status": "idle", "x": 0, "y": 0
    })
    client.post("/robots", json={
        "name": "Bot2", "battery": 80, "status": "moving", "x": 1, "y": 1
    })
    response = client.get("/robots")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_robot(client):
    robot_data = {"name": "Bot1", "battery": 90, "status": "idle", "x": 0, "y": 0}
    create_resp = client.post("/robots", json=robot_data)
    robot_id = create_resp.json()["id"]

    response = client.get(f"/robots/{robot_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bot1"
    assert data["id"] == robot_id


def test_get_robot_not_found(client):
    response = client.get("/robots/999")
    assert response.status_code == 404


def test_update_robot(client):
    robot_data = {"name": "Bot1", "battery": 90, "status": "idle", "x": 0, "y": 0}
    create_resp = client.post("/robots", json=robot_data)
    robot_id = create_resp.json()["id"]

    update_data = {"battery": 50, "status": "moving"}
    response = client.put(f"/robots/{robot_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["battery"] == 50
    assert data["status"] == "moving"
    assert data["name"] == "Bot1"


def test_update_robot_not_found(client):
    response = client.put("/robots/999", json={"battery": 50})
    assert response.status_code == 404


def test_delete_robot(client):
    robot_data = {"name": "Bot1", "battery": 90, "status": "idle", "x": 0, "y": 0}
    create_resp = client.post("/robots", json=robot_data)
    robot_id = create_resp.json()["id"]

    response = client.delete(f"/robots/{robot_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == robot_id

    # Verify it's gone
    get_resp = client.get(f"/robots/{robot_id}")
    assert get_resp.status_code == 404


def test_delete_robot_not_found(client):
    response = client.delete("/robots/999")
    assert response.status_code == 404
