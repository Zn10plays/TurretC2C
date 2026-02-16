import cv2
import time
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket

class CameraCapture(Subsystem):
    def __init__(self, bus, controller):
        super().__init__(bus)
        self.controller = controller
        self.cam = cv2.VideoCapture(0)

    async def start(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                continue

            t_capture = time.monotonic()

            packet = FramePacket(
                image=frame,
                timestamp=t_capture,
            )

            await self.bus.publish("frame", packet)
