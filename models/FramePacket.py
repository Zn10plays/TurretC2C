from dataclasses import dataclass
import numpy as np

@dataclass
class FramePacket():
    frame: np.ndarray
    timestamp: float
    pass
