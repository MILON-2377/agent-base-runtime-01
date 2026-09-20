from dataclasses import dataclass, field
from enum import Enum


class AttemptStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Attempt:
    attempt_id: str
    step_id: str
    status: AttemptStatus = AttemptStatus.PENDING
    lifecycle_history: list[AttemptStatus] = field(
        default_factory=lambda: [AttemptStatus.PENDING]
    )
