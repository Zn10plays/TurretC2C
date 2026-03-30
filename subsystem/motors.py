from subsystem.structure import Subsystem
from utility.loader import load_config, is_raspberry_pi
from models.MoveCommand import MoveCommand, CommandType
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

        # dynamic import for pi, selects the correct transport
        if is_raspberry_pi():
            import moteus_pi3hat

            self.transport = moteus_pi3hat.Pi3HatRouter(
                servo_bus_map={...},
            ) 
        else:
            self.transport = moteus.get_singleton_transport()

        # init controllers 
        self.pitch_motor = moteus.Controller(
            id=self.config['motors']['motorIds'][0], 
            transport=self.transport)
        
        self.yaw_motor = moteus.Controller(
            id=self.config['motors']['motorIds'][1], 
            transport=self.transport)


        bus.subscribe('MoveCommand', self.follow_command) # MoveCommand class

    # updates setpoints with a command
    def follow_command(self, orders: MoveCommand):

        if (self.e_stop):
            return
        
        if (orders.type == CommandType.FAULT):
            print('fault detected stopping motors')
            self.e_stop = True
            return

        self.command_type = orders.type
        self.setpoints = orders.setpoints

    # helper to push logs to the internal eventbus
    async def update_status(self, results, publish: bool = True):

        timestamp = time.monotonic_ns()
        position = [results[0].values[moteus.Register.POSITION], 
                    results[1].values[moteus.Register.POSITION]]
        
        velocity = [results[0].values[moteus.Register.VELOCITY], 
                    results[1].values[moteus.Register.VELOCITY]]

        if publish:
            await self.bus.publish('MotorLogs', MotorPositionLog(
            timestamp, position, velocity
        ))

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
                self.pitch_motor.make_position(
                    position=(self.setpoints[0] if self.command_type == CommandType.Position else math.nan),
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
