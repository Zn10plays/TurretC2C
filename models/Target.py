from dataclasses import dataclass

@dataclass
class TargetPacket():
    target_type: str
    target_id: str
    relative_pitch: float
    relative_yaw: float
    timestamp: float