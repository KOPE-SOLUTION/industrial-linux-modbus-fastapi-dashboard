# EP3 — FastAPI Web API

ใน EP3 เราจะต่อยอดจาก EP2 โดยนำฟังก์ชัน `read_sensor()` จาก `modbus_reader.py` มาเปิดเป็น REST API ด้วย FastAPI

เป้าหมายคือให้เครื่องอื่นในวง LAN สามารถเปิด Browser หรือเรียก API เพื่ออ่านค่าจาก Sensor ได้ เช่น

```text
http://192.168.1.125:8000/api/sensor
```

---

## ภาพรวมการทำงาน

```text
Modbus RTU Sensor
        ↓
USB-RS485 Adapter
        ↓
modbus_reader.py
        ↓
FastAPI app.py
        ↓
REST API
        ↓
Browser / Client / Dashboard
```

---

## โครงสร้างไฟล์ใน EP3

ตัวอย่างโครงสร้างโปรเจกต์:

```text
industrial-linux-modbus-fastapi-dashboard/
├── requirements.txt
└── src/
    ├── app.py
    └── modbus_reader.py
```

> หมายเหตุ: ในตัวอย่างนี้ติดตั้ง Python library ด้วย `pip` ภายใน `.venv` และรันคำสั่งจากภายในโฟลเดอร์ `src`

---

## 1. เข้าโฟลเดอร์โปรเจกต์

```bash
cd industrial-linux-modbus-fastapi-dashboard
```

---

## 2. ติดตั้ง Package ที่จำเป็นใน Virtual Environment

ถ้ายังไม่มี `.venv` ให้สร้างก่อน จากนั้นเปิดใช้งานแล้วติดตั้ง FastAPI, Uvicorn, pymodbus และ pyserial ด้วย `pip`

```bash
sudo apt update
sudo apt install python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pymodbus pyserial
```

บันทึกรายการ Package ไว้ใช้ซ้ำภายหลัง:

```bash
pip freeze > requirements.txt
```

ตรวจสอบว่า Package สำคัญใช้งานได้:

```bash
python -c "import fastapi; print('fastapi OK')"
python -c "import pymodbus; print('pymodbus OK')"
python -c "import serial; print('pyserial OK')"
```

---

## 3. ตรวจสอบไฟล์ modbus_reader.py จาก EP2

ไฟล์ `modbus_reader.py` ต้องมีฟังก์ชัน `read_sensor()` และเมื่อรันเดี่ยว ๆ ต้องอ่านค่าได้ก่อน

```bash
cd src
python modbus_reader.py
```

ตัวอย่างผลลัพธ์:

```json
{
  "status": "ok",
  "pm1_0": 9,
  "pm2_5": 16,
  "pm10": 20,
  "timestamp": 1783627165
}
```

ถ้าขั้นตอนนี้ยังอ่านไม่ได้ ให้แก้ `modbus_reader.py` ให้ทำงานก่อน แล้วค่อยไปต่อ FastAPI

---

## 4. สร้างไฟล์ app.py

สร้างไฟล์:

```bash
nano app.py
```

ใส่โค้ดนี้:

```python
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
        "health_api": "/api/health",
        "sensor_api": "/api/sensor"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/api/sensor")
def get_sensor():
    return read_sensor()
```

บันทึกไฟล์:

```text
Ctrl + O
Enter
Ctrl + X
```

---

## 5. รัน FastAPI Server

ถ้าอยู่ในโฟลเดอร์ `src` และเปิดใช้งาน `.venv` แล้ว ให้รัน:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

ถ้ารันสำเร็จ จะเห็นข้อความประมาณนี้:

```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 6. เปิดจาก Browser

จากเครื่อง PC หรือ Notebook ที่อยู่ในวง LAN เดียวกัน เปิด:

```text
http://192.168.1.125:8000
```

ควรได้ผลลัพธ์ประมาณนี้:

```json
{
  "message": "Modbus Sensor API is running",
  "docs": "/docs",
  "health_api": "/api/health",
  "sensor_api": "/api/sensor"
}
```

---

## 7. เปิด Swagger API Docs

FastAPI มีหน้า API Docs ให้อัตโนมัติ

เปิด:

```text
http://192.168.1.125:8000/docs
```

จะเห็น API ที่สร้างไว้ เช่น

```text
GET /
GET /api/health
GET /api/sensor
```

---

## 8. ทดสอบ Health API

เปิด:

```text
http://192.168.1.125:8000/api/health
```

ควรได้:

```json
{
  "status": "ok"
}
```

API นี้ใช้ตรวจสอบว่า Web Server ยังทำงานอยู่หรือไม่ โดยไม่ต้องอ่าน Sensor

---

## 9. ทดสอบ Sensor API

เปิด:

```text
http://192.168.1.125:8000/api/sensor
```

ควรได้ค่าประมาณนี้:

```json
{
  "status": "ok",
  "pm1_0": 9,
  "pm2_5": 16,
  "pm10": 20,
  "timestamp": 1783627165
}
```

เมื่อถึงจุดนี้ แปลว่า FastAPI สามารถเรียก `read_sensor()` จาก EP2 และส่งค่ากลับเป็น JSON ได้แล้ว

---

## 10. ทดสอบด้วย curl บน Linux gateway

เปิด Terminal อีกหน้าหนึ่ง หรือ SSH เข้าใหม่ แล้วรัน:

```bash
curl http://127.0.0.1:8000/api/health
```

และ:

```bash
curl http://127.0.0.1:8000/api/sensor
```

ถ้าอยู่บนเครื่อง PC ให้ใช้ IP ของ Linux gateway:

```bash
curl http://192.168.1.125:8000/api/sensor
```

---

## หมายเหตุเรื่องการรันจากตำแหน่งโฟลเดอร์

ถ้าอยู่ในโฟลเดอร์โปรเจกต์หลัก:

```text
industrial-linux-modbus-fastapi-dashboard/
```

และไฟล์อยู่ใน `src/app.py` ให้รันแบบนี้:

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

แต่ถ้าเข้าไปอยู่ในโฟลเดอร์ `src` แล้ว:

```bash
cd src
```

ให้รันแบบนี้:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

สรุป:

```text
อยู่ที่ root project  → uvicorn src.app:app --host 0.0.0.0 --port 8000
อยู่ที่ src/          → uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### 1. ModuleNotFoundError: No module named 'src'

สาเหตุคือรัน `uvicorn src.app:app` ตอนที่อยู่ในโฟลเดอร์ `src`

ให้เปลี่ยนเป็น:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

### 2. ModuleNotFoundError: No module named 'pymodbus'

แปลว่ายังไม่ได้ติดตั้ง `pymodbus` ใน `.venv` หรือยังไม่ได้ activate environment

แก้ด้วย:

```bash
source .venv/bin/activate
pip install pymodbus
```

---

### 3. RuntimeError: Serial client requires pyserial

แปลว่ายังไม่ได้ติดตั้ง `pyserial` ใน `.venv` หรือยังไม่ได้ activate environment

แก้ด้วย:

```bash
source .venv/bin/activate
pip install pyserial
```

---

### 4. read_input_registers() got an unexpected keyword argument 'slave'

`pymodbus` บางเวอร์ชันใช้ `device_id` แทน `slave`

ให้แก้ใน `modbus_reader.py` จาก:

```python
result = client.read_input_registers(
    address=START_REGISTER,
    count=REGISTER_COUNT,
    slave=SLAVE_ID
)
```

เป็น:

```python
result = client.read_input_registers(
    address=START_REGISTER,
    count=REGISTER_COUNT,
    device_id=SLAVE_ID
)
```

---

### 5. API `/api/sensor` ได้ 500 Internal Server Error

ให้ดู Log ใน Terminal ที่รัน `uvicorn`

ถ้า `/api/health` ใช้ได้ แต่ `/api/sensor` ใช้ไม่ได้ แปลว่า FastAPI ทำงานแล้ว แต่ส่วนอ่าน Sensor มีปัญหา

ให้ทดสอบไฟล์ `modbus_reader.py` โดยตรง:

```bash
python modbus_reader.py
```

ถ้าไฟล์นี้ยัง Error ต้องแก้จุดนี้ก่อน

---

### 6. เปิดจาก PC ไม่ได้

ตรวจสอบ IP ของ Linux gateway:

```bash
hostname -I
```

ตรวจสอบว่า Uvicorn รันด้วย:

```bash
--host 0.0.0.0
```

ไม่ใช่:

```bash
--host 127.0.0.1
```

เพราะ `127.0.0.1` จะเปิดได้เฉพาะในเครื่อง Linux gateway เอง

---

## สรุป EP3

ใน EP3 เราได้สร้าง FastAPI Web API เพื่อเปิดค่าจาก Sensor ผ่าน HTTP

API ที่ได้:

```text
GET /
GET /api/health
GET /api/sensor
```

ผลลัพธ์สุดท้าย:

```json
{
  "status": "ok",
  "pm1_0": 9,
  "pm2_5": 16,
  "pm10": 20,
  "timestamp": 1783627165
}
```

ข้อมูล JSON นี้จะถูกนำไปใช้ต่อใน EP4 เพื่อสร้างหน้าเว็บ HTML Dashboard
