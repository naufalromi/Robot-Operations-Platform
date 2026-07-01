import os
import json
import paho.mqtt.client as mqtt
from app import crud, database, schemas

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("fleet/robot/+/telemetry")

def on_message(client, userdata, msg):
    try:
        # Extract robot_id from topic
        topic_parts = msg.topic.split('/')
        robot_id = int(topic_parts[2])
        
        # Parse payload
        payload = json.loads(msg.payload.decode())
        robot_update = schemas.RobotUpdate(**payload)
        
        # Update database
        db = database.SessionLocal()
        try:
            crud.update_robot(db, robot_id, robot_update)
        finally:
            db.close()
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
