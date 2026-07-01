import random
from .. import schemas

class RobotSimulator:
    def simulate_step(self, robot: schemas.Robot) -> schemas.RobotUpdate:
        # Simple simulation logic: 
        # 1. Move robot by +/- 1 in x and y
        # 2. Drain battery by 1%
        new_x = robot.x + random.randint(-1, 1)
        new_y = robot.y + random.randint(-1, 1)
        new_battery = max(0, robot.battery - 1)

        return schemas.RobotUpdate(
            x=new_x,
            y=new_y,
            battery=new_battery
        )
