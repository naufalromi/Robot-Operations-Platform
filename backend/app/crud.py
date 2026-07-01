from sqlalchemy.orm import Session
from . import models, schemas


def get_robots(db: Session):
    return db.query(models.Robot).all()


def get_robot(db: Session, robot_id: int):
    return db.query(models.Robot).filter(models.Robot.id == robot_id).first()


def create_robot(db: Session, robot: schemas.RobotCreate):
    db_robot = models.Robot(**robot.model_dump())
    db.add(db_robot)
    db.commit()
    db.refresh(db_robot)
    return db_robot


def update_robot(db: Session, robot_id: int, robot: schemas.RobotUpdate):
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        return None
    update_data = robot.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_robot, key, value)
    db.commit()
    db.refresh(db_robot)
    return db_robot


def delete_robot(db: Session, robot_id: int):
    db_robot = get_robot(db, robot_id)
    if not db_robot:
        return None
    db.delete(db_robot)
    db.commit()
    return db_robot
