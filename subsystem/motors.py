from subsystem.structure import Subsystem
from utility.loader import load_config
from models.MoveCommand import MoveCommand, CommandType
from collections import deque
import math
import asyncio
import moteus
import time
from models.MotorStatus import MotorPositionLog

class MotorsSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        self.e_stop = False
        self.config = load_config()

        self.command_type: CommandType = CommandType.Coast
        self.setpoints = [0, 0]

        self.transport = moteus.get_singleton_transport()

        self.pitch_motor = moteus.Controller(id=self.config['motors']['motorIds'][0], transport=self.transport)
        self.yaw_motor = moteus.Controller(id=self.config['motors']['motorIds'][1], transport=self.transport)


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
        
        position[0] = results[0].values[moteus.Register.POSITION]
        position[1] = results[1].values[moteus.Register.POSITION]
        
        velocity[0] = results[0].values[moteus.Register.VELOCITY]
        velocity[1] = results[1].values[moteus.Register.VELOCITY]

        self.current_log = MotorPositionLog(
            timestamp, position, velocity
        )

        if publish:
            await self.bus.publish('motors', self.current_log)

    async def start(self):

        while True:
            if self.e_stop:
                # stop everything
                break

            if self.command_type == CommandType.FAULT or self.command_type == CommandType.Coast:
                results = await self.transport.cycle([
                    self.pitch_motor.make_stop(query=True),
                    self.yaw_motor.make_stop(query=True),
                ])

                await self.update_status(results)
                continue

            results = await self.transport.cycle([
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
