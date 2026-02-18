from models.MotorStatus import MotorPositionLog
import math
from typing import Deque

def interpolate_history_at_timestamp(self, query_ts: int, history) -> MotorPositionLog | None:
        """
        Linearly interpolate motor position and velocity at the given timestamp (ns).

        Returns:
            MotorPositionLog with interpolated values,
            or None if history is empty.
        """

        if not self.history:
            return None

        # If outside bounds, clamp to nearest sample
        if query_ts <= self.history[0].timestamp:
            return self.history[0]

        if query_ts >= self.history[-1].timestamp:
            return self.history[-1]

        # Find bracketing samples
        prev_log = None
        next_log = None

        for log in self.history:
            if log.timestamp >= query_ts:
                next_log = log
                break
            prev_log = log

        # Safety check (should not happen due to bounds checks)
        if prev_log is None or next_log is None:
            return None

        t0 = prev_log.timestamp
        t1 = next_log.timestamp

        # Avoid division by zero (shouldn't happen with monotonic clock)
        if t1 == t0:
            return prev_log

        # Linear interpolation factor
        alpha = (query_ts - t0) / (t1 - t0)

        # Interpolate position and velocity
        interp_position = []
        interp_velocity = []

        for i in range(2):  # since you stated len always 2
            p0 = prev_log.position[i]
            p1 = next_log.position[i]

            v0 = prev_log.velocity[i]
            v1 = next_log.velocity[i]

            # If either is NaN, propagate NaN
            if math.isnan(p0) or math.isnan(p1):
                interp_position.append(math.nan)
            else:
                interp_position.append(p0 + alpha * (p1 - p0))

            if math.isnan(v0) or math.isnan(v1):
                interp_velocity.append(math.nan)
            else:
                interp_velocity.append(v0 + alpha * (v1 - v0))

        return MotorPositionLog(
            timestamp=query_ts,
            position=interp_position,
            velocity=interp_velocity,
        )