import random
from .. import schemas

TASKS = ["Patrolling", "Inspecting", "Returning to Base", "Idle", "Scanning Area"]

class RobotSimulator:
    def simulate_step(self, robot: schemas.Robot) -> schemas.RobotUpdate:
        if robot.status == "Stopped":
            new_x = robot.x
            new_y = robot.y
            new_battery = max(0, robot.battery - 1)
            new_task = "Idle"
        elif robot.status == "Charging":
            new_x = robot.x
            new_y = robot.y
            new_battery = min(100, robot.battery + 2)
            new_task = "Charging"
        else:
            new_x = robot.x + random.randint(-1, 1)
            new_y = robot.y + random.randint(-1, 1)
            new_battery = max(0, robot.battery - 1)
            new_task = random.choice(TASKS)

        return schemas.RobotUpdate(
            x=new_x,
            y=new_y,
            battery=new_battery,
            task=new_task
        )
