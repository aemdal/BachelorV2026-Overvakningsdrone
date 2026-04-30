import json
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

class GPSService(QObject):

    position_updated = pyqtSignal(float, float) # Sender signal når GPS-posisjon oppdateres, sender latitude og longitude
    details_updated = pyqtSignal(dict) # Sender signal når GPS-detaljer oppdateres, sender en dict med detaljer

    def __init__(self, broker_ip: str, topic: str = "drone/drone-01/gps"):
        super().__init__()

        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect_async(broker_ip, 1883)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"MQTT-tilkobling vellykket, abonnerer på {self.topic}")
            client.subscribe(self.topic)
        else:
            print(f"MQTT-tilkobling feilet med kode {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            lat = data["lat"]
            lon = data["lon"]

            self.position_updated.emit(lat, lon)
            self.details_updated.emit(data)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Feil ved behandling av GPS-data: {e}")