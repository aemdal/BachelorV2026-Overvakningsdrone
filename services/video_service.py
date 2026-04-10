import cv2
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
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

        if self.cap.isOpened():
            self.cap = None
            self.connection_changed.emit(False)
            return
        
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        
        self.timer.start(33)
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
        
        ok, frame = self.cap.read()

        if not ok or frame is None:
            return
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame_ready.emit(rgb)