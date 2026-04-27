import cv2
import os
import numpy as np
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class VideoService(QObject):

    frame_ready = pyqtSignal(np.ndarray)
    connection_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.grab_frame)


    def connect(self, url: str):
        print("Prøver å koble til RTSP-strøm...")
        # self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

        # Prøver med TCP først for å redusere latency, fallback til UDP hvis det feiler
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

        if not self.cap.isOpened():
            print("Tilkobling feilet")
            self.cap = None
            self.connection_changed.emit(False)
            return
        
        print("Tilkobling vellykket")
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        
        self.timer.start(16) 
        self.connection_changed.emit(True)

    def disconnect(self):
        self.timer.stop()

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.connection_changed.emit(False)

    def grab_frame(self):
        if self.cap is None:
            return

        # Tester å tømme bufferet før vi leser for å redusere latency
        for _ in range(1):
            self.cap.grab()
        
        ok, frame = self.cap.read()

        if not ok or frame is None:
            return
        
        small = cv2.resize(frame, (640, 360))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        self.frame_ready.emit(rgb)