from dataclasses import dataclass, field
from enum import Enum


class RunStatus(Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"

    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class Run:
    run_id: str
    status: RunStatus = RunStatus.CREATED

    lifecycle_history: list[RunStatus] = field(
        default_factory=lambda: [RunStatus.CREATED]
    )
