from fastapi import FastAPI
from modbus_reader import read_sensor

app = FastAPI(
    title="Modbus Sensor API",
    description="Simple FastAPI server for reading Modbus RTU sensor data",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Modbus Sensor API is running",
        "docs": "/docs",
        "sensor_api": "/api/sensor"
    }


@app.get("/api/sensor")
def get_sensor():
    return read_sensor()


@app.get("/api/health")
def health_check():
    return {
        "status": "ok"
    }