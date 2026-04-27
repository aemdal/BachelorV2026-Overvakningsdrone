from machine import UART, Pin, I2C
from time import sleep, ticks_ms
from micropyGPS import MicropyGPS
import ujson

# =========================================================
# GPS CONFIG
# =========================================================
my_gps = MicropyGPS(location_formatting='dd')
gps_serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# =========================================================
# BNO055 CONFIG
# =========================================================
BNO055_ADDR = 0x29   
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

# =========================================================
# HJELPEFUNKSJONER GPS
# =========================================================
def signed_coord(coord):
    value = coord[0]
    hemi = coord[1]
    if hemi in ('S', 'W'):
        value = -value
    return value

def get_gps_data():
    if my_gps.valid:
        lat = signed_coord(my_gps.latitude)
        lon = signed_coord(my_gps.longitude)
    else:
        lat = None
        lon = None

    return {
        "valid": my_gps.valid,
        "lat": lat,
        "lon": lon,
        "altitude": my_gps.altitude,
        "satellites_in_use": my_gps.satellites_in_use,
        "hdop": my_gps.hdop,
        "timestamp": my_gps.timestamp,
        "date": my_gps.date
    }

# =========================================================
# HJELPEFUNKSJONER BNO055
# =========================================================
def write_reg(reg, value):
    i2c.writeto_mem(BNO055_ADDR, reg, bytes([value]))

def read_len(reg, n):
    return i2c.readfrom_mem(BNO055_ADDR, reg, n)

def twos_comp(val, bits):
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val

def read_chip_id():
    return i2c.readfrom_mem(BNO055_ADDR, 0x00, 1)[0]

def init_bno055():
    # CONFIGMODE
    write_reg(0x3D, 0x00)
    sleep(0.1)

    # NDOF mode
    write_reg(0x3D, 0x0C)
    sleep(0.1)

def read_euler():
    data = read_len(0x1A, 6)

    heading = twos_comp((data[1] << 8) | data[0], 16) / 16.0
    roll    = twos_comp((data[3] << 8) | data[2], 16) / 16.0
    pitch   = twos_comp((data[5] << 8) | data[4], 16) / 16.0

    return heading, roll, pitch

def read_calibration():
    calib = i2c.readfrom_mem(BNO055_ADDR, 0x35, 1)[0]

    sys_  = (calib >> 6) & 0x03
    gyro  = (calib >> 4) & 0x03
    acc   = (calib >> 2) & 0x03
    mag   = calib & 0x03

    return {
        "sys": sys_,
        "gyro": gyro,
        "acc": acc,
        "mag": mag
    }

def get_imu_data():
    yaw, roll, pitch = read_euler()
    calib = read_calibration()

    return {
        "yaw": yaw,
        "roll": roll,
        "pitch": pitch,
        "calib": calib
    }

# =========================================================
# INIT
# =========================================================
try:
    chip_id = read_chip_id()
    if chip_id != 0xA0:
        print(ujson.dumps({
            "type": "error",
            "message": "Unexpected BNO055 chip ID",
            "chip_id": chip_id
        }))
    else:
        print(ujson.dumps({
            "type": "status",
            "message": "BNO055 detected",
            "chip_id": chip_id
        }))
except Exception as e:
    print(ujson.dumps({
        "type": "error",
        "message": "BNO055 init failed",
        "details": str(e)
    }))

init_bno055()

seq = 0
last_send = ticks_ms()

# =========================================================
# MAIN LOOP
# =========================================================
while True:
    try:
        # ---- Oppdater GPS-parser med alle innkommende bytes
        while gps_serial.any():
            data = gps_serial.read()
            if data:
                for byte in data:
                    my_gps.update(chr(byte))

        # ---- Send samlet telemetripakke ca. 5 Hz
        now = ticks_ms()
        if now - last_send >= 200:
            last_send = now

            gps_data = get_gps_data()
            imu_data = get_imu_data()

            packet = {
                "type": "telemetry",
                "seq": seq,
                "t_ms": now,
                "gps": gps_data,
                "imu": imu_data
            }

            print(ujson.dumps(packet))
            seq += 1

    except Exception as e:
        print(ujson.dumps({
            "type": "error",
            "message": "Telemetry loop failed",
            "details": str(e)
        }))
        sleep(0.5)

    sleep(0.01)