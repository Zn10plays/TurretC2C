import math
from dataclasses import dataclass
from models.MotorStatus import MotorPositionLog
from models.MoveCommand import MoveCommand, CommandType

# ---- Configuration ----

PITCH_MIN_DEG = -10.0
PITCH_MAX_DEG = 45.0

THETA_C = (PITCH_MAX_DEG + PITCH_MIN_DEG) / 2.0
A = (PITCH_MAX_DEG - PITCH_MIN_DEG) / 2.0

OMEGA_P = math.sqrt(2)   # rad/sec
OMEGA_Y = 1.0            # rad/sec

DT_DEFAULT = 0.01


# ---- Data Model ----

@dataclass
class TurretState:
    pitch_pos: float   # deg
    pitch_vel: float   # deg/sec
    yaw_pos: float     # deg
    yaw_vel: float     # deg/sec


# ---- Trajectory Generator ----

class SurveyTrajectory:
    def __init__(self):
        self.initialized = False
        self.phi_p = 0.0
        self.phi_y = 0.0
        self.last_timestamp = None

    # ---------- Initialization ----------

    def _initialize_phase(self, current: MotorPositionLog):
        pitch = current.position[0]
        pitch_vel = current.velocity[0]
        yaw = current.position[1]

        # Normalize pitch into [-1, 1]
        x = (pitch - THETA_C) / A if A != 0 else 0.0
        x = max(-1.0, min(1.0, x))

        base = math.asin(x)

        # Resolve ambiguity using velocity
        if pitch_vel >= 0:
            self.phi_p = base
        else:
            self.phi_p = math.pi - base

        # Yaw phase directly from position
        self.phi_y = math.radians(yaw)

        self.last_timestamp = current.timestamp
        self.initialized = True

    def _compute_dt(self, current: MotorPositionLog):
        if self.last_timestamp is None:
            self.last_timestamp = current.timestamp
            return DT_DEFAULT

        dt = (current.timestamp - self.last_timestamp) / 1e9
        self.last_timestamp = current.timestamp

        if dt <= 0 or dt > 0.1:
            return DT_DEFAULT

        return dt

    # ---------- Core Step ----------

    def step(self, current: MotorPositionLog) -> TurretState:
        if not self.initialized:
            self._initialize_phase(current)

        dt = self._compute_dt(current)

        # Advance phase
        self.phi_p += OMEGA_P * dt
        self.phi_y += OMEGA_Y * dt

        # Wrap pitch phase (optional hygiene)
        if self.phi_p > 2 * math.pi:
            self.phi_p -= 2 * math.pi

        # ---- Kinematics ----

        pitch_pos = THETA_C + A * math.sin(self.phi_p)
        pitch_vel = A * OMEGA_P * math.cos(self.phi_p)

        yaw_pos = math.degrees(self.phi_y)
        yaw_vel = math.degrees(OMEGA_Y)

        return TurretState(
            pitch_pos=pitch_pos,
            pitch_vel=pitch_vel,
            yaw_pos=yaw_pos,
            yaw_vel=yaw_vel
        )


# ---- Command Adapters ----

def state_to_position_command(state: TurretState) -> MoveCommand:
    return MoveCommand(
        type=CommandType.Position,
        setpoints=[state.pitch_pos, state.yaw_pos]
    )


def state_to_velocity_command(state: TurretState) -> MoveCommand:
    return MoveCommand(
        type=CommandType.Velocity,
        setpoints=[state.pitch_vel, state.yaw_vel]
    )


def state_to_combined_command(state: TurretState) -> list[MoveCommand]:
    """
    If your downstream system supports multiple commands per cycle,
    or separate buses for pos/vel.
    """
    return [
        state_to_position_command(state),
        state_to_velocity_command(state)
    ]


# ---- Public Interface ----

trajectory = SurveyTrajectory()

def get_next_state(current_orientation: MotorPositionLog) -> TurretState:
    return trajectory.step(current_orientation)


def get_next_setpoint(
    current_orientation: MotorPositionLog,
    mode: CommandType = CommandType.Position
):
    state = get_next_state(current_orientation)

    if mode == CommandType.Position:
        return state_to_position_command(state)

    elif mode == CommandType.Velocity:
        return state_to_velocity_command(state)

    else:
        raise ValueError(f"Unsupported mode: {mode}")