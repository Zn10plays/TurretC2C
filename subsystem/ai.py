import time
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
from models.Target import TargetPacket
from ultralytics import YOLO
from utility.loader import load_config

class AiAnnotateSubsystem(Subsystem):
    def __init__(self, bus):
        self.config = load_config()

        self.threshold = self.config['detection']['threshold']
        self.model = YOLO(self.config['detection']['modelPath'])
        
        super().__init__(bus)

    async def process(self, packet: FramePacket):
        results = self.model(packet.frame, persist=True)

        result = results[0]

        if result.boxes is None:
            return

        for box in result.boxes:
            conf = float(box.conf.item())

            if conf < self.threshold:
                continue

            cls = int(box.cls.item())

            # Bounding box (pixel space)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Center pixel
            u = (x1 + x2) / 2.0
            v = (y1 + y2) / 2.0

            # Track ID (if tracking enabled)
            track_id = None
            if hasattr(box, "id") and box.id is not None:
                track_id = int(box.id.item())

            await self.bus.publish('targets', TargetPacket(
                timestamp=packet.timestamp,
                track_id=track_id,
                class_id=cls,
                confidence=conf,
                u=u,
                v=v,
                bbox=[x1, y1, x2, y2]
            ))

        # code go here
        pass

    async def start(self):
        self.bus.subscribe('frame', self.process)
        pass

