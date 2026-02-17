import cv2
import time
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
from utility.loader import load_config
import asyncio

class VisionSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)
        self.config = load_config()

        self.cam = cv2.VideoCapture(self.config['vision']['cameraID'])

    async def start(self):

        while True:
            ret, frame = await asyncio.to_thread(
                self.cam.read
            )

            if not ret:
                await asyncio.sleep(0.001)
                continue

            t_capture = time.monotonic()

            packet = FramePacket(
                frame=frame,
                timestamp=t_capture,
            )

            await self.bus.publish("frame", packet)
