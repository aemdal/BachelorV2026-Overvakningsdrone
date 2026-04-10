from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal

class ControlPanel(QWidget):

    ptz_command = pyqtSignal(str) # Sender signal for PTZ-kommandoer, sender kommando som streng

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Kamerakontroller")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Rad 1: Opp-knapp
        top_row = QHBoxLayout()
        self.up_button = QPushButton("▲")
        top_row.addWidget(self.up_button)
        top_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(top_row)

        # Rad 2: Venstre-, og høyreknapp
        middle_row = QHBoxLayout()
        self.left_button = QPushButton("◀")
        self.right_button = QPushButton("▶")
        middle_row.addWidget(self.left_button)
        middle_row.addWidget(self.right_button)
        layout.addLayout(middle_row)

        # Rad 3: Ned-knapp
        bottom_row = QHBoxLayout()
        self.down_button = QPushButton("▼")
        bottom_row.addWidget(self.down_button)
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(bottom_row)

        # Koble knapper til signaler
        self.up_button.clicked.connect(lambda: self.ptz_command.emit("up"))
        self.down_button.clicked.connect(lambda: self.ptz_command.emit("down"))
        self.left_button.clicked.connect(lambda: self.ptz_command.emit("left"))
        self.right_button.clicked.connect(lambda: self.ptz_command.emit("right"))