import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
)
from PyQt6.QtCore import Qt

from views.video_panel import VideoPanel
from views.control_panel import ControlPanel
from views.map_panel import MapPanel
from views.info_panel import InfoPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # -- Vindu setup --
        self.setWindowTitle("Dashboard - Bachelor v26")
        self.setMinimumSize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # -- Topplinje --
        toolbar_layout = QHBoxLayout()

        title_label = QLabel("Dashboard - Bachelor v26")
        toolbar_layout.addWidget(title_label)

        # -- Rullgardin for kameravalg --
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Rutenett", "Kamera 1", "Kamera 2", "Kamera 3", "Kamera 4"])
        toolbar_layout.addWidget(self.view_selector)

        # -- Knapper --
        self.detection_button = QPushButton("Objektgjenkjenning: AV")
        toolbar_layout.addWidget(self.detection_button)

        self.connect_button = QPushButton("Koble til")
        toolbar_layout.addWidget(self.connect_button)

        main_layout.addLayout(toolbar_layout)

        # -- Innholdsområde --
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # -- Venstre kolonne: Videostrøm og kamerakontroller --
        left_column = QVBoxLayout()
        
        # venstre kolonne - videostrøm
        self.video_panel = VideoPanel()
        left_column.addWidget(self.video_panel, stretch=3)

        # venstre kolonne - kamerakontroller
        self.control_panel = ControlPanel()
        left_column.addWidget(self.control_panel, stretch=1)


        content_layout.addLayout(left_column)

        # -- Høyre kolonne: Kart og informasjon --
        right_column = QVBoxLayout()

        # høyre kolonne - kart
        self.map_panel = MapPanel()
        right_column.addWidget(self.map_panel, stretch=1)

        # høyre kolonne - informasjon
        self.info_panel = InfoPanel()
        right_column.addWidget(self.info_panel, stretch=1)

        content_layout.addLayout(right_column)

        # -- Juster størrelsesforhold --
        content_layout.setStretch(0, 3)  # Venstre kolonne tar 3 ganger mer plass enn høyre
        content_layout.setStretch(1, 1)  # Høyre kolonne tar 1 del av plassen