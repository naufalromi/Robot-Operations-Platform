import asyncio
from sqlalchemy.orm import Session
from .. import crud, database
from .simulator import RobotSimulator

async def run_simulator():
    simulator = RobotSimulator()
    while True:
        # Use a new DB session for each iteration to avoid connection issues
        db = database.SessionLocal()
        try:
            robots = crud.get_robots(db)
            for robot in robots:
                # Only simulate 'active' or 'idle' robots, not 'broken' ones
                if robot.status != "Broken":
                    update_data = simulator.simulate_step(robot)
                    crud.update_robot(db, robot.id, update_data)
        finally:
            db.close()
        
        # Wait 5 seconds before next simulation step
        await asyncio.sleep(5)
