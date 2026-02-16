from subsystem.structure import Subsystem
from utility.loader import load_config
from models.MoveCommand import MoveCommand, CommandType
import moteus

class CameraCapture(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        self.e_stop = False
        self.config = load_config()

        self.command_type: CommandType = CommandType.Coast
        self.setpoints = [0, 0]

        # note ids in yaw, pitch, roll 
        self.motors = [moteus.Controller(id) 
                       for id in self.config['motors']['motorIds']]
        
        bus.subscribe('MoveCommand', self.follow_command)

    def follow_command(self, orders: MoveCommand):

        if (self.e_stop):
            return
        
        if (orders.type == CommandType.FAULT):
            self.e_stop = True
            return

        self.command_type = orders.type
        self.setpoints = orders.setpoints
        pass


    async def start(self):
        while True:
            if self.e_stop:
                # stop everything
                break



            






