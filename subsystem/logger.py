from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
import cv2
import asyncio


class LoggerSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)
        self.latest_frame = None
        self.running = True

    async def handle_log_frames(self, packet: FramePacket):
        # Just store the frame
        self.latest_frame = packet.frame

    async def start(self):
        self.bus.subscribe('frame', self.handle_log_frames)

        cv2.namedWindow("camera", cv2.WINDOW_NORMAL)

        while self.running:
            if self.latest_frame is not None:
                cv2.imshow("camera", self.latest_frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                self.running = False
                break

            await asyncio.sleep(0.01)  # yield to event loop

        cv2.destroyAllWindows()
