from dataclasses import dataclass

@dataclass
class GPSData:
    latitude: float
    longitude: float
    altitude: float
    satellites: int

@dataclass
class DetectionData:
    object_type: str
    confidence: float
    bounding_box: tuple

@dataclass
class DroneState:
    drone_id: str
    name: str
    
    is_connected: bool = False
    rtsp_url: str = ""

    gps_data: GPSData = None

    battery_level: int = 0
    temperature: float = 0.0
    weather_condition: str = ""

    detections: list[DetectionData] = None
    detection_enabled: bool = False

    distance_to_target: float = 0.0