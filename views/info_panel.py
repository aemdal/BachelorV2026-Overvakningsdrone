from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal

class InfoPanel(QWidget):

    object_selected = pyqtSignal(int) # Sender signal når et objekt velges, sender objekt-ID

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Informasjonspanel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Batteristatus
        battery_label = QLabel("Batteri")
        layout.addWidget(battery_label)
        self.battery_value = QLabel("Ukjent..")
        layout.addWidget(self.battery_value)

        # GPS-posisjon
        gps_label = QLabel("GPS-koordinater")
        layout.addWidget(gps_label)
        self.gps_value = QLabel("Ukjent..")
        layout.addWidget(self.gps_value)

        # Temperatur
        temp_label = QLabel("Temperatur")
        layout.addWidget(temp_label)
        self.temp_value = QLabel("Ukjent..")
        layout.addWidget(self.temp_value)

        # Avstand til objekt
        distance_label = QLabel("Avstand til objekt")
        layout.addWidget(distance_label)
        self.distance_value = QLabel("Ukjent..")
        layout.addWidget(self.distance_value)

        # Liste over detekterte objekter
        objects_label = QLabel("Gjenkjente objekter")
        layout.addWidget(objects_label)
        
        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.on_object_clicked)
        layout.addWidget(self.object_list)

    def update_battery(self, percent: int):
        self.battery_value.setText(f"{percent}%")
        
    def update_gps(self, lat: float, lon: float):
        self.gps_value.setText(f"{lat:.6f}, {lon:.6f}")
        
    def update_temperature(self, temp: float):
        self.temp_value.setText(f"{temp:.1f}°C")

    def update_distance(self, meters: float):
        self.distance_value.setText(f"{meters:.2f} m")
        
    def update_objects(self, objects: list):
        self.object_list.clear()
        for object in objects:
            item = QListWidgetItem(object)
            self.object_list.addItem(item)
        
    def on_object_clicked(self, item: QListWidgetItem):
        index = self.object_list.row(item)
        self.object_selected.emit(index)

