import requests
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class WeatherService(QObject):

    temperature_updated = pyqtSignal(float) # Sender signal når temperaturen oppdateres, sender temperatur i Celsius

    def __init__(self):
        super().__init__()

        self.lat = None
        self.lon = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_weather)
        self.timer.start(300000) # Hent værdata hvert 5. minutt

    def update_position(self, lat: float, lon: float):
        first_position = self.lat is None

        self.lat = lat
        self.lon = lon

        if first_position:
            self.fetch_weather() # Hent værdata umiddelbart ved første posisjonsoppdatering

    def fetch_weather(self):
        if self.lat is None or self.lon is None:
            return
        
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.lat}"
                f"&longitude={self.lon}"
                f"&current_weather=true"
            )
            print(f"URL: {url}")

            response = requests.get(url, timeout=5)
            data = response.json()
            print(f"API-svar: {data}")

            temp = data["current_weather"]["temperature"]
            self.temperature_updated.emit(temp)
            print(f"Værdata oppdatert: {temp}°C")

        except Exception as e:
            print(f"Feil ved innhenting av værdata: {e}")