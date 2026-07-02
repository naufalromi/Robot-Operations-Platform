import random
from .. import schemas

class RobotSimulator:
    def simulate_step(self, robot: schemas.Robot) -> schemas.RobotUpdate:
        # Check status to determine behavior
        if robot.status == "Stopped":
            # Robot stopped, no movement, battery drains slightly
            new_x = robot.x
            new_y = robot.y
            new_battery = max(0, robot.battery - 0) # Stopped, no movement drain
        elif robot.status == "Charging":
            # Robot charging, no movement, battery increases
            new_x = robot.x
            new_y = robot.y
            new_battery = min(100, robot.battery + 5) # Charging
        else:
            # Default (Moving)
            new_x = robot.x + random.randint(-1, 1)
            new_y = robot.y + random.randint(-1, 1)
            new_battery = max(0, robot.battery - 1)

        return schemas.RobotUpdate(
            x=new_x,
            y=new_y,
            battery=new_battery
        )
