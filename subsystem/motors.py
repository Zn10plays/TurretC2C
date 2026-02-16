from subsystem.structure import Subsystem
from utility.loader import load_config
from models.MoveCommand import MoveCommand, CommandType
from collections import deque
from typing import Deque
import math
import moteus
from dataclasses import dataclass

@dataclass
class MotorPostionLogs():
    timestamp: float
    position: float # in deg of output shaft
    velocity: float # in deg/sec
    accleration: float # in deg/sec^2

class CameraCapture(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        self.e_stop = False
        self.config = load_config()
        self.history: Deque[MotorPostionLogs] = deque([], maxlen=50)

        self.command_type: CommandType = CommandType.Coast
        self.setpoints = [0, 0]

        self.pitch_motor = moteus.Controller(self.config['motors']['motorIds'][0])
        self.yaw_motor = moteus.Controller(self.config['motors']['motorIds'][1])

        bus.subscribe('MoveCommand', self.follow_command)

    def follow_command(self, orders: MoveCommand):

        if (self.e_stop):
            return
        
        if (orders.type == CommandType.FAULT):
            self.e_stop = True
            return

        self.command_type = orders.type
        self.setpoints = orders.setpointss

    async def start(self):

        transport = moteus.get_singleton_transport()

        while True:
            if self.e_stop:
                # stop everything
                break

            if self.command_type == CommandType.FAULT or self.command_type == CommandType.Coast:
                results = await transport.cycle([
                    self.pitch_motor.make_position(position=math.nan, query=True),
                    self.yaw_motor.make_position(position=math.nan, query=True),
                ])



