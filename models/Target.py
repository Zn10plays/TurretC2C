from dataclasses import dataclass

@dataclass
class TargetPacket():
    timestamp: float
    track_id: int | None
    class_id: int
    confidence: float
    u: float
    v: float
    bbox: list[float]