import numpy as np
from ultralytics import YOLO
from PyQt6.QtCore import QObject, pyqtSignal

class DetectionService(QObject):

    detections_ready = pyqtSignal(list)

    def __init__(self, model_path="yolov8m.pt"):
        super().__init__()
        
        self.model = YOLO(model_path)
        self.enabled = False
        self.detect_every_n_frames = 10
        self._frame_count = 0

    def process_frame(self, frame: np.ndarray):
        if not self.enabled:
            return
            
        self._frame_count += 1

        if self._frame_count % self.detect_every_n_frames != 0:
            return
            
        results = self.model.predict(
            source=frame,
            conf=0.5,
            imgsz=640,
            verbose=False,
            device="cpu", # kan skiftes til cuda for å bruke GPU
        )

        detections = []
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "box": (int(x1), int(y1), int(x2), int(y2))
            })
        self.detections_ready.emit(detections)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.detections_ready.emit([])

        

