## EP3: FastAPI Web API

เป้าหมาย EP3 คือเอา `read_sensor()` จาก EP2 มาเปิดเป็น API:

```bash
http://192.168.1.125:8000/api/sensor
```

---

## 1. เข้าโฟลเดอร์โปรเจกต์

```bash
cd raspberry-pi-modbus-fastapi-dashboard
source .venv/bin/activate
```

## 2. ติดตั้ง FastAPI

```bash
pip install fastapi uvicorn
```

<br>

บันทึก package:

```bash
pip freeze > requirements.txt
```

## 3. สร้างไฟล์ src/app.py

```bash
nano src/app.py
```

<br>

ใส่โค้ดนี้:

```py
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
```

---

## 4. รัน FastAPI

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

---

## 5. เปิดจาก Browser

บนเครื่อง PC เปิด:

```bash
http://192.168.1.125:8000
```

<br>

ดู API docs:

```bash
http://192.168.1.125:8000/docs
```

<br>

อ่านค่า Sensor:

```bash
http://192.168.1.125:8000/api/sensor
```

<br>

ควรได้ประมาณ:

```json
{
  "status": "ok",
  "pm1_0": 8,
  "pm2_5": 15,
  "pm10": 18,
  "timestamp": 1783625509
}
```

---

## ถ้าเจอ import error

ถ้า `from modbus_reader import read_sensor` ไม่เจอ ให้รันแบบนี้แทน:

```bash
cd src
uvicorn app:app --host 0.0.0.0 --port 8000
```