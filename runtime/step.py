from dataclasses import dataclass, field
from enum import Enum

from .attempt import Attempt


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Step:
    step_id: str
    run_id: str
    status: StepStatus = StepStatus.PENDING
    lifecycle_history: list[StepStatus] = field(
        default_factory=lambda: [StepStatus.PENDING]
    )
    attempts: list[Attempt] = field(default_factory=list)
