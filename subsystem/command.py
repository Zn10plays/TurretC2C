from subsystem.structure import Subsystem
from enum import Enum
import asyncio
from models.MotorStatus import MotorPositionLog
from utility.paths import get_next_setpoint
from models.MoveCommand import CommandType
import time

class ControlMode(Enum):
    Idle: 1
    Survey: 2
    TeleOp: 3
    LockOn: 4

class CommandSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)

        # start of doing nothing
        self.current_state = ControlMode.Idle
        
        self.bus.subscribe('ChangeControlState', self.update_control_state)
        self.bus.subscribe('MotorLogs', self.update_current_motor_setpoints)

        # init 90 deg pitch, no yaw, no velocity
        self.current_turret_pos = MotorPositionLog(time.monotonic_ns(), [0.25, 0], [0, 0])
    
    def update_control_state(self, new_state: ControlMode):
        self.current_state = new_state
        pass

    def update_current_motor_setpoints(self, motor_logs: MotorPositionLog):
        self.current_turret_pos = motor_logs
        pass

    async def start(self):
        while True:
            match self.current_state:
                case ControlMode.Idle:
                    # do nothing
                    pass
                case ControlMode.Survey:
                    cmd = get_next_setpoint(
                        self.current_turret_pos,
                        mode=CommandType.Position  # or Velocity
                    )
                    self.bus.publish("MoveCommand", cmd)
                case ControlMode.TeleOp:
                    # go to user command, or do nothing
                    # fire is always a user command
                    pass
                case ControlMode.LockOn:
                    # follow target, cascade pid with moteus
                    # issue is, we need to fid the target
                    pass
            
            await asyncio.sleep(0.01)
                