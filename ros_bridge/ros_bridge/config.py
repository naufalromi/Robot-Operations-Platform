import os


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

DEFAULT_ROBOT_ID = int(os.getenv("ROBOT_ID", "1"))
DEFAULT_X = float(os.getenv("INITIAL_X", "0.0"))
DEFAULT_Y = float(os.getenv("INITIAL_Y", "0.0"))
DEFAULT_BATTERY = float(os.getenv("INITIAL_BATTERY", "100.0"))

SIMULATION_RATE = float(os.getenv("SIMULATION_RATE", "1.0"))
BATTERY_DRAIN_RATE = float(os.getenv("BATTERY_DRAIN_RATE", "0.5"))
BATTERY_CHARGE_RATE = float(os.getenv("BATTERY_CHARGE_RATE", "2.0"))
MOVE_SPEED = float(os.getenv("MOVE_SPEED", "1.0"))
