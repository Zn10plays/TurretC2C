from dataclasses import dataclass
import numpy as np

@dataclass
class MotorPostions():
    current_yaw: float
    current_pitch: float
    timestamp: float
    pass

@dataclass
class FramePacket():
    frame: np.ndarray
    timestamp: float
    motor_positons: MotorPostions
    pass
