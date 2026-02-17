import asyncio
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
from models.Target import TargetPacket
from utility.loader import load_config
from workers.ultralytics import run_inference


class AiAnnotateSubsystem(Subsystem):
    def __init__(self, bus, process_pool):
        self.config = load_config()
        self.threshold = self.config['detection']['threshold']
        self.model_path = self.config['detection']['modelPath']
        self.pool = process_pool

        super().__init__(bus)

    async def process(self, packet: FramePacket):
        loop = asyncio.get_running_loop()

        detections = await loop.run_in_executor(
            self.pool,
            run_inference,
            packet.frame,
            self.model_path,
            self.threshold
        )

        for det in detections:
            await self.bus.publish('targets', TargetPacket(
                timestamp=packet.timestamp,
                track_id=det["track_id"],
                class_id=det["class_id"],
                confidence=det["confidence"],
                u=det["u"],
                v=det["v"],
                bbox=det["bbox"]
            ))

    async def start(self):
        self.bus.subscribe('frame', self.process)
