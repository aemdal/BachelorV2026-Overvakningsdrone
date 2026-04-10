import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from services.video_service import VideoService

BROKER_IP = "100.82.60.17"
RTSP_URL = f"rtsp://{BROKER_IP}:8554/test"

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # Opprett VideoService og koble den til MainWindow
    video_service = VideoService()
    video_service.frame_ready.connect(window.video_panel.update_frame)

    # Koble knapper til service-funksjoner
    window.connect_button.clicked.connect(lambda: video_service.connect(RTSP_URL))

    
    window.show()
    return app.exec()
    


if __name__ == "__main__":
    raise SystemExit(main())