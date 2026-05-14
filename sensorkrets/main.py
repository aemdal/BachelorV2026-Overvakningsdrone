from machine import UART, Pin, I2C
from time import sleep, ticks_ms, ticks_diff
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
# RANGEFINDER CONFIG
# =========================================================
# GP12 = Pico TX -> Rangefinder RX
# GP13 = Pico RX <- Rangefinder TX
rf_uart = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))

MEASURE_CMD = bytes([0xAE, 0xA7, 0x04, 0x00, 0x05, 0x09, 0xBC, 0xBE])

# Pushbutton: GP14 -> knapp -> GND
button = Pin(14, Pin.IN, Pin.PULL_UP)
last_button_state = 1

last_range_result = {
    "valid": False,
    "distance_m": None,
    "raw_distance": None,
    "source": None,
    "t_ms": None,
    "error": "no_measurement_yet"
}

# =========================================================
# GPS HELPERS
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
# BNO055 HELPERS
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
    write_reg(0x3D, 0x00)  # CONFIGMODE
    sleep(0.1)

    write_reg(0x3D, 0x0C)  # NDOF mode
    sleep(0.1)

def read_euler():
    data = read_len(0x1A, 6)

    heading = twos_comp((data[1] << 8) | data[0], 16) / 16.0
    roll    = twos_comp((data[3] << 8) | data[2], 16) / 16.0
    pitch   = twos_comp((data[5] << 8) | data[4], 16) / 16.0

    return heading, roll, pitch

def read_calibration():
    calib = i2c.readfrom_mem(BNO055_ADDR, 0x35, 1)[0]

    return {
        "sys":  (calib >> 6) & 0x03,
        "gyro": (calib >> 4) & 0x03,
        "acc":  (calib >> 2) & 0x03,
        "mag":  calib & 0x03
    }

def get_imu_data():
    yaw, roll, pitch = read_euler()

    return {
        "yaw": yaw,
        "roll": roll,
        "pitch": pitch,
        "calib": read_calibration()
    }

# =========================================================
# RANGEFINDER HELPERS
# =========================================================
def clear_rf_uart():
    while rf_uart.any():
        rf_uart.read()

def send_measure_command():
    clear_rf_uart()
    rf_uart.write(MEASURE_CMD)
    rf_uart.flush()

def read_rf_frame(timeout_ms=1000):
    start = ticks_ms()
    buf = b""

    while ticks_diff(ticks_ms(), start) < timeout_ms:
        if rf_uart.any():
            chunk = rf_uart.read()
            if chunk:
                buf += chunk

                start_idx = buf.find(b"\xAE\xA7")
                end_idx = buf.find(b"\xBC\xBE")

                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    return buf[start_idx:end_idx + 2]

        sleep(0.005)

    return None

def parse_range_frame(frame):
    if frame is None:
        return {
            "valid": False,
            "distance_m": None,
            "raw_distance": None,
            "error": "timeout"
        }

    if len(frame) < 10:
        return {
            "valid": False,
            "distance_m": None,
            "raw_distance": None,
            "error": "frame_too_short"
        }

    if frame[0:2] != b"\xAE\xA7":
        return {
            "valid": False,
            "distance_m": None,
            "raw_distance": None,
            "error": "bad_header"
        }

    if frame[-2:] != b"\xBC\xBE":
        return {
            "valid": False,
            "distance_m": None,
            "raw_distance": None,
            "error": "bad_footer"
        }

    if frame[4] != 0x85:
        return {
            "valid": False,
            "distance_m": None,
            "raw_distance": None,
            "error": "unexpected_response_code",
            "response_code": frame[4]
        }

    # Basert på validert respons:
    # AE A7 17 00 85 00 00 00 48 ...
    # frame[7:9] = avstand, big-endian, oppløsning 0.1 m
    raw_distance = (frame[7] << 8) | frame[8]
    distance_m = raw_distance / 10.0

    return {
        "valid": True,
        "distance_m": distance_m,
        "raw_distance": raw_distance,
        "error": None
    }

def perform_range_measurement(source="button"):
    send_measure_command()
    frame = read_rf_frame()
    result = parse_range_frame(frame)

    result["source"] = source
    result["t_ms"] = ticks_ms()

    return result

def handle_button():
    global last_button_state, last_range_result

    current_state = button.value()

    # Falling edge: 1 -> 0 betyr knapp trykket
    if last_button_state == 1 and current_state == 0:
        sleep(0.03)  # debounce

        if button.value() == 0:
            last_range_result = perform_range_measurement("button")

            # Vent til knappen slippes
            while button.value() == 0:
                sleep(0.01)

    last_button_state = current_state

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

        # ---- Sjekk lokal knapp for rangefinder-trigger
        handle_button()

        # ---- Send samlet telemetripakke ca. 5 Hz
        now = ticks_ms()
        if ticks_diff(now, last_send) >= 200:
            last_send = now

            packet = {
                "type": "telemetry",
                "seq": seq,
                "t_ms": now,
                "gps": get_gps_data(),
                "imu": get_imu_data(),
                "rangefinder": last_range_result
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