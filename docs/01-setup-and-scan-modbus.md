# คู่มือการสแกน Modbus RTU ด้วย Linux Edge Gateway และ RS485 Interface

## วัตถุประสงค์

คู่มือนี้อธิบายการเตรียม Linux gateway เพื่อค้นหา (Scan) Modbus Address ของอุปกรณ์ RS485 ผ่าน RS485 Interface ซึ่งอาจเป็น Built-in RS485 ในเครื่อง Industrial Linux Gateway หรือ USB-RS485 Adapter

> Note: ซีรีส์นี้เน้นทำระบบจริงให้ทำงานได้ก่อน บางช่วงจะใช้วิธีคัดลอกคำสั่งหรือโค้ดตัวอย่างไปวาง แล้วอธิบายภาพรวมของ workflow เป็นหลัก รายละเอียดเชิงลึกของ HTML, CSS, JavaScript, Python, FastAPI, systemd และ Podman สามารถแยกศึกษาเป็นซีรีส์พื้นฐานเพิ่มเติมภายหลังได้

---
# 1. อัปเดตระบบ

```bash
sudo apt update
```

---

# 2. ติดตั้งโปรแกรมที่จำเป็น

ติดตั้งโปรแกรมระบบที่จำเป็น แล้วสร้าง Python virtual environment สำหรับติดตั้ง Library ด้วย `pip`

```bash
sudo apt install python3-venv mbpoll -y
python3 -m venv .venv
source .venv/bin/activate
pip install pyserial
```

---

# 3. ตรวจสอบว่า Linux gateway พบ RS485 Interface แล้ว

```bash
# USB-RS485 Adapter
ls -l /dev/ttyUSB*

# Built-in RS485 บางรุ่นอาจใช้ชื่อเหล่านี้
ls -l /dev/ttyS* /dev/ttyAMA* /dev/ttyO* 2>/dev/null
```

ตัวอย่างผลลัพธ์

```text
crw-rw---- 1 root dialout 188, 0 Jun 30 12:53 /dev/ttyUSB0
crw-rw---- 1 root dialout   4, 65 Jun 30 12:53 /dev/ttyS1
```

หากพบ device path เช่น `/dev/ttyUSB0` หรือ `/dev/ttyS1` แสดงว่า Linux gateway มองเห็น RS485 Interface แล้ว ให้นำ path ที่เจอจริงไปใช้ในคำสั่ง `mbpoll` และค่า `SERIAL_PORT` ใน Python

---

# 4. ตรวจสอบสิทธิ์ของผู้ใช้

```bash
groups
```

ควรมี

```text
dialout
```

เช่น

```text
pi0001 adm dialout cdrom sudo audio video plugdev users gpio i2c spi
```

หากไม่มี `dialout`

```bash
sudo usermod -aG dialout $USER
```

จากนั้น Logout และ Login ใหม่

---

# 5. ทดสอบเปิด Serial Port

```bash
# เปลี่ยน /dev/ttyUSB0 เป็น serial port จริงของเครื่อง เช่น /dev/ttyS1
python -c "import serial; s=serial.Serial('/dev/ttyUSB0',9600,timeout=1); print('OK'); s.close()"
```

ผลลัพธ์ที่ถูกต้อง

```text
OK
```

---

# 6. สแกน Modbus Address

ตัวอย่างนี้ใช้

* Baud Rate : 9600
* Data Bits : 8
* Parity : None
* Stop Bits : 1
* Function Code : 04 (Read Input Registers)

สแกน Address 1–20

```bash
for id in $(seq 1 20); do
    echo "Scan ID $id"
    mbpoll -m rtu -b 9600 -P none -a $id -t 4 -r 1 -c 1 /dev/ttyUSB0 -1 -q && echo "FOUND $id"
done

# ถ้าเป็น Built-in RS485 ให้เปลี่ยน /dev/ttyUSB0 เป็น path จริง เช่น /dev/ttyS1
```

---

# 7. ตัวอย่างผลลัพธ์

กรณีไม่พบอุปกรณ์

```text
Scan ID 5
Read input register failed: Connection timed out
```

หมายความว่า

* ไม่มีอุปกรณ์ที่ Address นี้
* หรือ Baud Rate / Function Code ไม่ถูกต้อง

---

กรณีพบอุปกรณ์

```text
Scan ID 1
-- Polling slave 1...
[1]: 4

FOUND 1
```

หมายความว่า

* พบ Modbus Device
* Modbus Address = 1
* อ่าน Register สำเร็จ

---

# 8. หากไม่พบอุปกรณ์

ตรวจสอบตามลำดับ

* ตรวจสอบไฟเลี้ยง Sensor
* ตรวจสอบสาย RS485 A/B ไม่สลับ
* ตรวจสอบ Baud Rate
* ตรวจสอบ Modbus Address
* ทดลอง Function Code 03 หากอุปกรณ์รุ่นนั้นเก็บค่าไว้ใน Holding Register
* ทดลอง Register Address อื่น

---

# 9. ทดลอง Function Code 03

อุปกรณ์บางรุ่นเก็บค่าที่ต้องอ่านไว้ใน Holding Register แทน Input Register

ตัวอย่าง

```bash
for id in $(seq 1 20); do
    echo "Scan ID $id"
    mbpoll -m rtu -b 9600 -P none -a $id -t 3 -r 1 -c 1 /dev/ttyUSB0 -1 -q && echo "FOUND $id"
done

# ถ้าเป็น Built-in RS485 ให้เปลี่ยน /dev/ttyUSB0 เป็น path จริง เช่น /dev/ttyS1
```

หาก FC04 ไม่พบ แต่ FC03 พบ แสดงว่าอุปกรณ์ใช้ **Holding Register**

---

# 10. ความหมายของ Function Code

| Function Code | รายละเอียด               |
| ------------: | ------------------------ |
|            01 | Read Coils               |
|            02 | Read Discrete Inputs     |
|            03 | Read Holding Registers   |
|            04 | Read Input Registers     |
|            05 | Write Single Coil        |
|            06 | Write Single Register    |
|            15 | Write Multiple Coils     |
|            16 | Write Multiple Registers |

โดยทั่วไป

* **FC03** ใช้อ่านค่าที่สามารถเขียนได้ เช่น การตั้งค่า (Configuration)
* **FC04** ใช้อ่านค่าที่วัดได้จากเซนเซอร์ เช่น ความเร็วลม อุณหภูมิ ความชื้น ความดัน และค่าจากเซนเซอร์ต่าง ๆ

---

# 11. ขั้นตอนถัดไป

เมื่อทราบแล้วว่า

* Serial Port เช่น `/dev/ttyUSB0` สำหรับ USB-RS485 หรือ `/dev/ttyS1` สำหรับ Built-in RS485
* Baud Rate เท่าใด
* Modbus Address เท่าใด
* ใช้ Function Code 03 หรือ 04

ก็สามารถนำข้อมูลไปพัฒนาโปรแกรม Python หรือ FastAPI เพื่ออ่านค่าและแสดงผลผ่านหน้าเว็บได้ต่อไป
