from subsystem.structure import Subsystem

# the brains of the whole thing, this is the most fun part
# assuming vision work as intended
class AutoAim(Subsystem):
    def __call__(self, bus):
        super().__init__(bus)
    
    def start(self):
        pass

