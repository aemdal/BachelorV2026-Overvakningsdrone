import json
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject

class PTZService(QObject):

    def __init__(self, broker_ip: str, topic: str = "drone/drone-01/ptz/command"):
        super().__init__()

        self.topic = topic
        self.steps_per_command = 10
        self.client = mqtt.Client()
        self.client.connect_async(broker_ip, 1883)
        self.client.loop_start()

    def send_command(self, direction: str):
        if direction in ("left", "right"):
            axis = "pan"
        elif direction in ("up", "down"):
            axis = "tilt"
        else:
            return
        
        command = {
            "axis": axis,
            "direction": direction,
            "steps": self.steps_per_command
        }
        self.client.publish(self.topic, json.dumps(command))