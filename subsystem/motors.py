from subsystem.structure import Subsystem
from utility.loader import load_config
from models.MoveCommand import MoveCommand, CommandType
from collections import deque
import math
import asyncio
import moteus
import time
from models.MotorStatus import MotorPostionLog

class MotorControllers(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        self.e_stop = False
        self.config = load_config()

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
        self.setpoints = orders.setpoints

    async def update_status(self, results, publish: bool = True):
        timestamp = time.monotonic_ns()
        position = [math.nan, math.nan]
        velocity = [math.nan, math.nan]

        for result in results:
            index = result.source

            position[index] = result[moteus.Register.POSITION]
            velocity[index] = result[moteus.Register.VELOCITY]

        if publish:
            await self.bus.publish('motors', self.current_log)

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

                self.update_status(results)
                continue

            results = await transport.cycle([
                self.pitch_motor.make_position(position=(self.setpoints[0] if self.command_type == CommandType.Position else math.nan),
                    velocity=(self.setpoints[0] if self.command_type == CommandType.Velocity else math.nan),
                    accel_limit=self.config['motors']['accelerationLimits'][0],
                    query=True),

                self.yaw_motor.make_position(
                    position=(self.setpoints[1] if self.command_type == CommandType.Position else math.nan),
                    velocity=(self.setpoints[1] if self.command_type == CommandType.Velocity else math.nan),
                    accel_limit=self.config['motors']['accelerationLimits'][1],
                    query=True),
            ])

            await self.update_status(results)
            await asyncio.sleep(0.01)
