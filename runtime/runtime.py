from .attempt import Attempt, AttemptStatus
from .attempt_state_machine import AttemptStateMachine
from .execution import ExecutionResult
from .executor import Executor
from .run import Run, RunStatus
from .state_machine import RunStateMachine
from .step import Step, StepStatus
from .step_state_machine import StepStateMachine


class Runtime:
    def __init__(
        self,
        state_machine: RunStateMachine,
        step_state_machine: StepStateMachine,
        attempt_state_machine: AttemptStateMachine,
        executor: Executor,
    ):

        self.state_machine = state_machine
        self.step_state_machine = step_state_machine
        self.attempt_state_machine = attempt_state_machine
        self.executor = executor

    def transition_run(self, run: Run, target_state: RunStatus) -> bool:

        is_valid = self.state_machine.is_valid_transition(run.status, target_state)

        if not is_valid:
            return False

        run.status = target_state
        run.lifecycle_history.append(target_state)

        return True

    def transition_step(self, step: Step, target_state: StepStatus):

        is_valid = self.step_state_machine.is_valid_transition(
            step.status, target_state
        )

        if not is_valid:
            return False

        step.status = target_state
        step.lifecycle_history.append(target_state)

        return True

    def transition_attempt(self, attempt: Attempt, target_state: AttemptStatus) -> bool:

        is_valid = self.attempt_state_machine.is_valid_transition(
            attempt.status, target_state
        )

        if not is_valid:
            return False

        attempt.status = target_state
        attempt.lifecycle_history.append(target_state)

        return True

    def execute_step(self, step: Step, step_defination: str) -> ExecutionResult:

        is_valid = self.step_state_machine.is_valid_transition(
            step.status, StepStatus.RUNNING
        )

        if not is_valid:
            return ExecutionResult(
                success=False, error="Step cannot transition to RUNNING"
            )

        self.transition_step(step, StepStatus.RUNNING)

        attempt = Attempt(
            attempt_id=f"{step.step_id}-attempt-{len(step.attempts) + 1}",
            step_id=step.step_id,
        )

        step.attempts.append(attempt)

        is_valid_attempt_transition = self.attempt_state_machine.is_valid_transition(
            attempt.status, AttemptStatus.RUNNING
        )

        if not is_valid_attempt_transition:
            return ExecutionResult(
                success=False, error="Attempt cannot transition to RUNNING"
            )

        self.transition_attempt(attempt, AttemptStatus.RUNNING)

        try:
            result = self.execute_step(step, step_defination)

        except Exception as exc:
            result = ExecutionResult(success=False, error=str(exc))

        if result.success:
            self.transition_attempt(attempt, AttemptStatus.SUCCEEDED)

            self.transition_step(step, StepStatus.COMPLETED)

        else:
            self.transition_attempt(attempt, AttemptStatus.FAILED)

            self.transition_step(step, StepStatus.FAILED)

        return result
