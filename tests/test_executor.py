from runtime.execution import ExecutionResult
from runtime.executor import Executor
from runtime.step import Step, StepStatus


class MockExecutor(Executor):
    def execute(self, step: Step, step_defination: str) -> ExecutionResult:
        return ExecutionResult(success=True, output=f"Executed: {step_defination}")


def test_mock_executor_returns_successful_execution_result():

    executor = MockExecutor()

    step = Step(step_id="step-123", run_id="run-123")

    result = executor.execute(step, "search hotels")

    assert result.success is True
    assert result.output == "Executed: search hotels"

    assert result.error is None

    assert step.status == StepStatus.PENDING
