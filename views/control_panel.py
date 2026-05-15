from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QTimer


class ControlPanel(QWidget):

    ptz_command = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Pan/Tilt-kontroll (W/A/S/D)")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Rad 1 – opp
        top_row = QHBoxLayout()
        self.up_button = QPushButton("▲ W")
        top_row.addWidget(self.up_button)
        top_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(top_row)

        # Rad 2 – venstre og høyre
        middle_row = QHBoxLayout()
        self.left_button = QPushButton("◄ A")
        self.right_button = QPushButton("► D")
        middle_row.addWidget(self.left_button)
        middle_row.addWidget(self.right_button)
        layout.addLayout(middle_row)

        # Rad 3 – ned
        bottom_row = QHBoxLayout()
        self.down_button = QPushButton("▼ S")
        bottom_row.addWidget(self.down_button)
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(bottom_row)

        # set med aktive retninger for å håndtere kontinuerlig bevegelse
        self.active_directions = set()

        # Timer for kontinuerlig bevegelse
        self.repeat_timer = QTimer(self)
        self.repeat_timer.setInterval(100)
        self.repeat_timer.timeout.connect(self.send_repeat_command)
        self.active_direction = None

        # Koble knapper til press/release
        for button, direction in [
            (self.up_button, "up"),
            (self.down_button, "down"),
            (self.left_button, "left"),
            (self.right_button, "right"),
        ]:
            button.pressed.connect(lambda d=direction: self.start_command(d))
            button.released.connect(self.stop_command)

    def start_command(self, direction: str):
        self.active_directions.add(direction)
        self.ptz_command.emit(direction)
        if not self.repeat_timer.isActive():
            self.repeat_timer.start()

    def stop_command(self, direction: str):
        self.active_directions.discard(direction)
        if not self.active_directions:
            self.repeat_timer.stop()

    def send_repeat_command(self):
        for direction in self.active_directions:
            self.ptz_command.emit(direction)