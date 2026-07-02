import asyncio
import os
import json

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client
    try:
        import paho.mqtt.client as mqtt
        _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        _client.on_connect = lambda c, u, f, rc, p: None
        _client.on_message = lambda c, u, m: None
        _client.connect(MQTT_BROKER, 1883, 60)
        _client.loop_start()
        return _client
    except Exception as e:
        print(f"MQTT not available for simulator: {e}")
        return None


async def run_simulator():
    from .simulator import RobotSimulator
    from .. import crud, database, schemas

    simulator = RobotSimulator()
    while True:
        db = database.SessionLocal()
        try:
            robots = crud.get_robots(db)
            for robot in robots:
                if robot.status != "Broken":
                    update_data = simulator.simulate_step(robot)
                    topic = f"fleet/robot/{robot.id}/telemetry"
                    payload_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
                    payload_dict["id"] = robot.id
                    payload = json.dumps(payload_dict)
                    client = get_client()
                    if client:
                        client.publish(topic, payload)
        finally:
            db.close()

        await asyncio.sleep(5)
