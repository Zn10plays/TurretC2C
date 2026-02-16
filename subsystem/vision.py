import cv2
import time
import moteus
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket, MotorPostions

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

            result = await self.controller.set_position(
                position=float("nan"), query=True)

            motor_angle = result.values[moteus.Register.POSITION]

            packet = FramePacket(
                image=frame,
                timestamp=t_capture,
                motor_angle=motor_angle,
            )

            await self.bus.publish("frame", packet)
