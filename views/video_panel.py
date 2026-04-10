from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QPainter,
    QColor,
    QPen,
)
import numpy as np

class VideoPanel(QWidget):

    object_clicked = pyqtSignal(int) # Sender signal når et objekt klikkes, sender objekt-ID

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.video_label = QLabel("Videostrøm frakoblet")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)

        self.detections = [] # Liste for å lagre deteksjonsdata

    def update_frame(self, frame: np.ndarray):
        rgb = frame
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        pixmap = self.draw_crosshair(pixmap)

        scaled = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled)

    def draw_crosshair(self, pixmap: QPixmap) -> QPixmap:
        painter = QPainter(pixmap)

        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)

        center_x = pixmap.width() // 2
        center_y = pixmap.height() // 2
        size = 20

        painter.drawLine(center_x - size, center_y, center_x + size, center_y)
        painter.drawLine(center_x, center_y - size, center_x, center_y + size)

        painter.end()
        return pixmap
