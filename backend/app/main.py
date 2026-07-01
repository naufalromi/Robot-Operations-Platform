from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database, crud
from .simulator.manager import run_simulator
import asyncio

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_simulator())


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/robots", response_model=list[schemas.Robot])
def get_robots(db: Session = Depends(get_db)):
    return crud.get_robots(db)


@app.get("/robots/{robot_id}", response_model=schemas.Robot)
def get_robot(robot_id: int, db: Session = Depends(get_db)):
    robot = crud.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot


@app.post("/robots", response_model=schemas.Robot, status_code=201)
def create_robot(robot: schemas.RobotCreate, db: Session = Depends(get_db)):
    return crud.create_robot(db, robot)


@app.put("/robots/{robot_id}", response_model=schemas.Robot)
def update_robot(robot_id: int, robot: schemas.RobotUpdate, db: Session = Depends(get_db)):
    updated = crud.update_robot(db, robot_id, robot)
    if not updated:
        raise HTTPException(status_code=404, detail="Robot not found")
    return updated


@app.delete("/robots/{robot_id}", response_model=schemas.Robot)
def delete_robot(robot_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_robot(db, robot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Robot not found")
    return deleted
