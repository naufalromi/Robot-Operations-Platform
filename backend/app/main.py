from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database, crud
from .simulator.manager import run_simulator
import asyncio
import json
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.active_connections.remove(conn)


manager = ConnectionManager()

_mqtt_client = None
_loop = None


def get_mqtt_client():
    global _mqtt_client
    if _mqtt_client is not None:
        return _mqtt_client
    try:
        import paho.mqtt.client as mqtt
        MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
        _mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        _mqtt_client.on_message = _on_mqtt_message
        _mqtt_client.connect(MQTT_BROKER, 1883, 60)
        _mqtt_client.subscribe("fleet/robot/+/telemetry")
        _mqtt_client.loop_start()
        return _mqtt_client
    except Exception as e:
        print(f"MQTT not available: {e}")
        return None


def _on_mqtt_message(client, userdata, msg):
    global _loop
    payload = msg.payload.decode()
    if _loop:
        asyncio.run_coroutine_threadsafe(manager.broadcast(payload), _loop)


ENABLE_PYTHON_SIM = os.getenv("ENABLE_PYTHON_SIM", "true").lower() == "true"


@app.on_event("startup")
async def startup_event():
    global _loop
    _loop = asyncio.get_running_loop()
    get_mqtt_client()
    if ENABLE_PYTHON_SIM:
        asyncio.create_task(run_simulator())
        print("Python simulator started (ENABLE_PYTHON_SIM=true)")
    else:
        print("Python simulator disabled (ENABLE_PYTHON_SIM=false) - using ROS2")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/robots", response_model=list[schemas.Robot])
def get_robots(db: Session = Depends(get_db)):
    return crud.get_robots(db)


@app.get("/robots/{robot_id}", response_model=schemas.Robot)
def get_robot(robot_id: int, db: Session = Depends(get_db)):
    robot = crud.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot


@app.post("/robots", response_model=schemas.Robot, status_code=201)
def create_robot(robot: schemas.RobotCreate, db: Session = Depends(get_db)):
    return crud.create_robot(db, robot)


@app.put("/robots/{robot_id}", response_model=schemas.Robot)
def update_robot(robot_id: int, robot: schemas.RobotUpdate, db: Session = Depends(get_db)):
    updated = crud.update_robot(db, robot_id, robot)
    if not updated:
        raise HTTPException(status_code=404, detail="Robot not found")
    return updated


@app.delete("/robots/{robot_id}", response_model=schemas.Robot)
def delete_robot(robot_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_robot(db, robot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Robot not found")
    return deleted


@app.post("/robots/{robot_id}/command")
def send_robot_command(robot_id: int, command: schemas.RobotCommand, db: Session = Depends(get_db)):
    robot = crud.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")

    client = get_mqtt_client()
    if not client:
        raise HTTPException(status_code=503, detail="MQTT broker not available")

    topic = f"fleet/robot/{robot_id}/command"
    payload = json.dumps({"command": command.command})
    client.publish(topic, payload, qos=1)

    if command.command == "DELETE":
        crud.delete_robot(db, robot_id)
    else:
        status_map = {"STOP": "Stopped", "CHARGE": "Charging", "RESUME": "Moving"}
        new_status = status_map.get(command.command)
        if new_status:
            crud.update_robot(db, robot_id, schemas.RobotUpdate(status=new_status))

    return {"sent": command.command, "topic": topic}
