from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
try:
    from .modbus_reader import read_sensor
except ImportError:
    from modbus_reader import read_sensor

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Modbus Sensor API",
    description="Simple FastAPI server for reading Modbus RTU sensor data",
    version="0.1.0"
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/sensor")
def get_sensor():
    return read_sensor()


@app.get("/api/health")
def health_check():
    return {
        "status": "ok"
    }