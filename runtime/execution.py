from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionResult:
    success: bool
    output: Any | None = None
    error: str | None = None
