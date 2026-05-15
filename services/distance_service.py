import json
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

class DistanceService(QObject):

    distance_updated = pyqtSignal(float)

    def __init__(self, broker_ip: str, topic: str = "drone/drone-01/distance"):
        super().__init__()
        
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect_async(broker_ip, 1883)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Avstand koblet til MQTT-broker og abonnerer på {self.topic}")
            client.subscribe(self.topic)
    
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            distance = data["distance_m"]
            self.distance_updated.emit(distance)
        except json.JSONDecodeError:
            print("Feil ved dekoding av avstandsdata")
        except KeyError:
            print("Mangler 'distance_m' i avstandsdata")