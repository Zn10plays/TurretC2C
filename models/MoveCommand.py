from dataclasses import dataclass
from enum import Enum

class CommandType(Enum):
    FAULT = 1 # pray to aulla this does not go off

    Coast = 2 # setpoints are null
    Position = 3 # setpoints are in digerees
    Velocity = 4 # deg/sec
    Acceleration = 5 # deg/sec^2
    Torque = 6 # Nm


@dataclass
class MoveCommand:
    type: CommandType
    setpoints: list[float]