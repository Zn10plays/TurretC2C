from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
from models.Target import TargetPacket
import cv2
import asyncio


class LoggerSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)
        self.latest_frame = None
        self.running = True
        self.targets = {}   # track_id -> TargetPacket

    async def handle_log_frames(self, packet: FramePacket):
        self.latest_frame = packet.frame.copy()

    async def handle_targets(self, packet: TargetPacket):
        # store latest target per track id
        self.targets[packet.track_id] = packet

    def draw_targets(self, frame):
        for target in self.targets.values():
            x1, y1, x2, y2 = target.bbox

            # Draw bounding box
            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2
            )

            label = f"ID:{target.track_id} {target.confidence:.2f}"

            cv2.putText(
                frame,
                label,
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return frame

    async def start(self):
        self.bus.subscribe('frame', self.handle_log_frames)
        self.bus.subscribe('targets', self.handle_targets)

        cv2.namedWindow("camera", cv2.WINDOW_NORMAL)

        while self.running:
            if self.latest_frame is not None:
                frame = self.latest_frame.copy()
                frame = self.draw_targets(frame)
                cv2.imshow("camera", frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                self.running = False
                break

            await asyncio.sleep(0.01)

        cv2.destroyAllWindows()