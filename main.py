import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from services.video_service import VideoService
from services.detection_service import DetectionService
from services.gps_service import GPSService

BROKER_IP = "100.82.60.17"
RTSP_URL = f"rtsp://{BROKER_IP}:8554/cam"

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # Opprett services
    video_service = VideoService()
    detection_service = DetectionService()
    gps_service = GPSService(broker_ip=BROKER_IP)

    # Video: service -> view
    video_service.frame_ready.connect(window.video_panel.update_frame)

    # Video: service -> deteksjon
    video_service.frame_ready.connect(detection_service.process_frame)

    # Deteksjon: service -> view
    detection_service.detections_ready.connect(window.video_panel.update_detections)

    # Deteksjon: service -> info panel
    detection_service.detections_ready.connect(
        lambda dets: window.info_panel.update_objects(
            [f"{d['class_name']} ({d['confidence']:.0%})" for d in dets]
        )
    )

    # GPS: service -> kart
    gps_service.position_updated.connect(window.map_panel.update_position)

    # GPS: service -> info panel
    gps_service.position_updated.connect(window.info_panel.update_gps)

    # Koble til knapp
    window.connect_button.clicked.connect(lambda: video_service.connect(RTSP_URL))

    # Deteksjon av/på knapp
    window.detection_button.clicked.connect(
        lambda: detection_service.set_enabled(not detection_service.enabled)
    )

    
    window.show()
    return app.exec()
    


if __name__ == "__main__":
    raise SystemExit(main())