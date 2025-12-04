from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import databases, sqlalchemy

DATABASE_URL = "sqlite:///./data.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

measurements = sqlalchemy.Table("measurements", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("soil", sqlalchemy.Integer),
    sqlalchemy.Column("temp", sqlalchemy.Float),
    sqlalchemy.Column("hum", sqlalchemy.Float),
    sqlalchemy.Column("time", sqlalchemy.DateTime, default=datetime.utcnow),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI(title="ESP32 Soil Station")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class DataIn(BaseModel):
    soil: int
    temp: float
    hum: float

@app.post("/data")
async def receive(data: DataIn):
    query = measurements.insert().values(
        soil=data.soil,
        temp=data.temp,
        hum=data.hum
    )
    await database.execute(query)
    return {"status": "ok"}

@app.get("/history")
async def get_history():
    query = measurements.select().order_by(measurements.c.id.desc).limit(200)
    return await database.fetch_all(query)