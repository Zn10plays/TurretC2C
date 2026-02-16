from subsystem.structure import Subsystem
from utility.loader import load_config

import moteus

class CameraCapture(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        self.e_stop = False

        self.config = load_config()

        # note ids in yaw, pitch, roll 
        self.motors = [moteus.Controller(id) 
                       for id in self.config['motors']['motorIds']]
        
        bus.subscribe('command', self.follow_command)

    def follow_command():
        pass


    def start(self):
        while True:
            if self.e_stop:
                break


