import time
from subsystem.structure import Subsystem
from models.FramePacket import FramePacket

class AiAnnotate(Subsystem):
    def __init__(self, bus, controller):
        super().__init__(bus)
        self.controller = controller

    def process(frame: FramePacket):
        pass

    async def start(self):
        pass

