import asyncio
import os
import json
import paho.mqtt.client as mqtt
from .. import crud, database, schemas
from .simulator import RobotSimulator

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

async def run_simulator():
    simulator = RobotSimulator()
    while True:
        # We only simulate; we don't update DB directly anymore
        db = database.SessionLocal()
        try:
            robots = crud.get_robots(db)
            for robot in robots:
                if robot.status != "Broken":
                    update_data = simulator.simulate_step(robot)
                    
                    # Publish telemetry via MQTT instead of DB update
                    topic = f"fleet/robot/{robot.id}/telemetry"
                    payload = update_data.model_dump_json()
                    client.publish(topic, payload)
        finally:
            db.close()
        
        # Wait 5 seconds before next simulation step
        await asyncio.sleep(5)
