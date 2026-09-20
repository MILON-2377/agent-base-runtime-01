from abc import ABC, abstractmethod

from .execution import ExecutionResult
from .step import Step


class Executor(ABC):
    @abstractmethod
    def execute(self, step: Step, step_defination: str) -> ExecutionResult:
        pass
