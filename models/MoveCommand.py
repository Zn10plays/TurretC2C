from dataclasses import dataclass
from enum import Enum

class CommandType(Enum):
    FAULT = -1 # pray to aulla this does not go off
    Coast = 0
    Position = 1
    Velocity = 2
    Acceleration = 3
    Torque = 4
    Path = 5


@dataclass
class MoveCommand:
    type: CommandType
    setpoints: list[float]