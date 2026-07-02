from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class RobotBase(BaseModel):
    name: str | None = None
    battery: float
    status: str | None = None
    x: float
    y: float
    task: str | None = None


class RobotCreate(RobotBase):
    pass


class RobotUpdate(BaseModel):
    name: str | None = None
    battery: float | None = None
    status: str | None = None
    x: float | None = None
    y: float | None = None
    task: str | None = None


class Robot(RobotBase):
    id: int
    last_heartbeat: datetime

    model_config = {"from_attributes": True}


class RobotCommand(BaseModel):
    command: Literal['STOP', 'CHARGE', 'RESUME', 'DELETE']
