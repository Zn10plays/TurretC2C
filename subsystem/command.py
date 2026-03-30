from subsystem.structure import Subsystem
from enum import Enum
import time

class ControlMode(Enum):
    Survey: 1
    Idle: 2
    LockOn: 3
    TeleOp: 4


class CommandSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        # start of doing nothing
        self.current_state = ControlMode.Idle
    
    def start(self):
        return super().start()
    

    

        