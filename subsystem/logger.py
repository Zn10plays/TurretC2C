from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
import cv2

class LoggerSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)


    async def hande_log_frames(self, packet: FramePacket):
        cv2.imshow('image', packet.frame)
        pass
    
    def start(self):
        self.bus.subscribe('frame', self.hande_log_frames)