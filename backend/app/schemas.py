from pydantic import BaseModel
from datetime import datetime


class RobotBase(BaseModel):
    name: str | None = None
    battery: int
    status: str | None = None
    x: int
    y: int
    task: str | None = None


class RobotCreate(RobotBase):
    pass


class RobotUpdate(BaseModel):
    name: str | None = None
    battery: int | None = None
    status: str | None = None
    x: int | None = None
    y: int | None = None
    task: str | None = None


class Robot(RobotBase):
    id: int
    last_heartbeat: datetime

    model_config = {"from_attributes": True}
