import os
import json
import paho.mqtt.client as mqtt
import time
from app import crud, database, schemas

# Force immediate flush for logs
os.environ["PYTHONUNBUFFERED"] = "1"

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
print(f"DEBUG: Starting MQTT Worker. Broker: {MQTT_BROKER}")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("DEBUG: Connected to MQTT broker successfully")
        client.subscribe("fleet/robot/+/telemetry")
        client.subscribe("fleet/robot/+/command")
    else:
        print(f"DEBUG: Failed to connect, return code {reason_code}")

def on_message(client, userdata, msg):
    print(f"DEBUG: Received message on {msg.topic}")
    try:
        topic_parts = msg.topic.split('/')
        if len(topic_parts) < 4:
            return
        topic_type = topic_parts[3]
        robot_id = int(topic_parts[2])
        payload = json.loads(msg.payload.decode())
        
        db = database.SessionLocal()
        try:
            if topic_type == "telemetry":
                robot_update = schemas.RobotUpdate(**payload)
                crud.update_robot(db, robot_id, robot_update)
            elif topic_type == "command":
                command = schemas.RobotCommand(**payload).command
                status = "Moving"
                if command == "STOP":
                    status = "Stopped"
                elif command == "CHARGE":
                    status = "Charging"
                elif command == "RESUME":
                    status = "Moving"
                crud.update_robot(db, robot_id, schemas.RobotUpdate(status=status))
        finally:
            db.close()
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# Exponential backoff for connection
while True:
    try:
        print("DEBUG: Attempting to create and connect MQTT client...")
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_forever()
    except Exception as e:
        print(f"DEBUG: Connection error: {e}. Retrying in 5 seconds...")
        time.sleep(5)
