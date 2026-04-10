from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QUrl, QTimer


class MapPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.map_view = QWebEngineView()
        self.map_view.setMinimumSize(300, 250)
        layout.addWidget(self.map_view)

        QTimer.singleShot(500, self.load_map)

    def load_map(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet"
                  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
            </script>
            <style>
                html, body { height: 100%; margin: 0; }
                #map { height: 100%; width: 100%; }

                .pulse-marker {
                    width: 16px;
                    height: 16px;
                    background: #007AFF;
                    border: 3px solid white;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%   { box-shadow: 0 0 0 0 rgba(0,122,255,0.6); }
                    70%  { box-shadow: 0 0 0 15px rgba(0,122,255,0); }
                    100% { box-shadow: 0 0 0 0 rgba(0,122,255,0); }
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const map = L.map('map').setView([59.9139, 10.7522], 13);

                L.tileLayer(
                    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    { maxZoom: 19,
                      attribution: '&copy; OpenStreetMap contributors' }
                ).addTo(map);

                const pulseIcon = L.divIcon({
                    className: 'pulse-marker',
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                });

                const marker = L.marker([59.9139, 10.7522],
                    { icon: pulseIcon }).addTo(map);

                function updatePosition(lat, lon) {
                    marker.setLatLng([lat, lon]);
                    map.setView([lat, lon]);
                }

                window.updatePosition = updatePosition;
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(html, baseUrl=QUrl("https://unpkg.com/"))

    def update_position(self, lat: float, lon: float):
        self.map_view.page().runJavaScript(f"updatePosition({lat}, {lon});")