from .common import CommonController
from .emergency import EmergencyController
from .device_detector import DeviceDetector
from .mouse_controller import MouseController

class Utils:
    def __init__(self):
        self.common = CommonController()
        self.emergency = EmergencyController()
        self.device_detector = DeviceDetector()
        self.mouse = MouseController()
