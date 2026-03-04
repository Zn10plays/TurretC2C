from dataclasses import dataclass

@dataclass
class MotorPositionLog():
    timestamp: float
    position: list[float] # in deg of output shaft
    velocity: list[float] # in deg/sec of the output shaft