from subsystem.bus import EventBus

class Subsystem:
    def __init__(self, bus: EventBus):
        self.bus = bus

    async def start(self):
        raise NotImplementedError
