# EP4 — HTML Dashboard

เป้าหมาย EP4 คือทำหน้าเว็บให้เปิดที่: `http://192.168.1.125:8000`

แล้วแสดงค่า Sensor โดยดึงจาก: `/api/sensor`

---

## 1. สร้างโฟลเดอร์

เข้าไปที่โฟลเดอร์ `src` ของโปรเจกต์ แล้วสร้างโฟลเดอร์สำหรับ HTML และ CSS:

```bash
cd industrial-linux-modbus-fastapi-dashboard/src
mkdir -p templates static
```

---

## 2. แก้ `app.py`

```bash
nano app.py
```

แทนโค้ดด้วยชุดนี้:

```py
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
```

---

## 3. สร้าง `templates/index.html`

```bash
nano templates/index.html
```

<br>

ใส่โค้ดนี้:

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Modbus Sensor Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <main class="container">
        <section class="header">
            <h1>Modbus Sensor Dashboard</h1>
            <p>Linux Edge Gateway + RS485 + FastAPI</p>
        </section>

        <section class="status-card">
            <span id="status-dot" class="dot"></span>
            <span id="status-text">Connecting...</span>
        </section>

        <section class="grid">
            <div class="card">
                <h2>PM1.0</h2>
                <div class="value">
                    <span id="pm1_0">--</span>
                    <small>ug/m3</small>
                </div>
            </div>

            <div class="card highlight">
                <h2>PM2.5</h2>
                <div class="value">
                    <span id="pm2_5">--</span>
                    <small>ug/m3</small>
                </div>
            </div>

            <div class="card">
                <h2>PM10</h2>
                <div class="value">
                    <span id="pm10">--</span>
                    <small>ug/m3</small>
                </div>
            </div>
        </section>

        <section class="footer">
            <p>Last Update: <span id="updated">--</span></p>
        </section>
    </main>

    <script>
        async function loadSensorData() {
            try {
                const response = await fetch("/api/sensor");
                const data = await response.json();

                if (data.status === "ok") {
                    document.getElementById("pm1_0").textContent = data.pm1_0;
                    document.getElementById("pm2_5").textContent = data.pm2_5;
                    document.getElementById("pm10").textContent = data.pm10;

                    const date = new Date(data.timestamp * 1000);
                    document.getElementById("updated").textContent =
                        date.toLocaleString("th-TH");

                    document.getElementById("status-text").textContent = "Online";
                    document.getElementById("status-dot").className = "dot online";
                } else {
                    document.getElementById("status-text").textContent = "Sensor Error";
                    document.getElementById("status-dot").className = "dot error";
                }
            } catch (error) {
                document.getElementById("status-text").textContent = "Connection Error";
                document.getElementById("status-dot").className = "dot error";
            }
        }

        loadSensorData();
        setInterval(loadSensorData, 1000);
    </script>
</body>
</html>
```

---

## 4. สร้าง `static/style.css`

ใส่โค้ดนี้:

```css
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #172033;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 32px 20px;
}

.header {
    text-align: center;
    margin-bottom: 28px;
}

.header h1 {
    margin: 0;
    font-size: 36px;
}

.header p {
    color: #64748b;
}

.status-card {
    background: white;
    border-radius: 18px;
    padding: 16px 20px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-weight: bold;
}

.dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #94a3b8;
}

.dot.online {
    background: #22c55e;
}

.dot.error {
    background: #ef4444;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.card {
    background: white;
    border-radius: 22px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
}

.card.highlight {
    transform: scale(1.04);
}

.card h2 {
    margin: 0 0 14px;
    color: #334155;
}

.value span {
    font-size: 56px;
    font-weight: bold;
}

.value small {
    display: block;
    margin-top: 8px;
    color: #64748b;
    font-size: 18px;
}

.footer {
    text-align: center;
    margin-top: 28px;
    color: #64748b;
}

@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .card.highlight {
        transform: none;
    }
}
```

---

## 5. รัน Server ใหม่

ถ้า server เดิมยังรันอยู่ ให้กด:

```bash
Ctrl + C
```

<br>

แล้วรันใหม่ โดยเปิดใช้งาน `.venv` ก่อน:

```bash
source ../.venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 6. เปิดหน้า Dashboard

เปิดจาก PC:

```bash
http://192.168.1.125:8000
```

ควรเห็น Dashboard และค่าอัปเดตทุก 1 วินาที

---

## เช็ก API เดิมยังอยู่

```bash
http://192.168.1.125:8000/api/sensor
```

<br>

และ Docs:

```bash
http://192.168.1.125:8000/docs
```