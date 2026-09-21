from .attempt import Attempt, AttemptStatus
from .attempt_state_machine import AttemptStateMachine
from .execution import ExecutionResult
from .executor import Executor
from .retry_policy import FailureContext, RetryDecision, RetryPolicy
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
        retry_policy: RetryPolicy,
    ):

        self.state_machine = state_machine
        self.step_state_machine = step_state_machine
        self.attempt_state_machine = attempt_state_machine
        self.executor = executor
        self.retry_policy = retry_policy

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
            result = self._execute_attempt(step, attempt, step_defination)

        except Exception as exc:
            result = ExecutionResult(success=False, error=str(exc))

        if result.success:
            self.transition_attempt(attempt, AttemptStatus.SUCCEEDED)
            self.transition_step(step, StepStatus.COMPLETED)
        else:
            self.transition_attempt(
                attempt,
                AttemptStatus.FAILED,
            )

        decision = self._decide_retry(
            step,
            attempt,
            result,
        )

        if decision.should_retry:
            next_attempt = self._create_attempt(step)
            self._start_attempt(next_attempt)

        else:
            self.transition_step(step, StepStatus.FAILED)

        return result

    def _build_failure_context(
        self, step: Step, attempt: Attempt, result: ExecutionResult
    ) -> FailureContext:

        return FailureContext(
            attempt_number=len(step.attempts),
            error_type="ExecutionError",
            error_code=result.error_code,
            error_message=result.error,
            operation=step.step_id,
        )

    def _decide_retry(
        self, step: Step, attempt: Attempt, result: ExecutionResult
    ) -> RetryDecision:

        failure_context = self._build_failure_context(step, attempt, result)

        return self.retry_policy.decide(failure=failure_context)

    def _create_attempt(self, step: Step) -> Attempt:

        attempt = Attempt(
            attempt_id=f"{step.step_id}-attempt-{len(step.attempts) + 1}",
            step_id=step.step_id,
        )

        step.attempts.append(attempt)

        return attempt

    def _start_attempt(self, attempt: Attempt) -> bool:

        return self.transition_attempt(attempt, AttemptStatus.RUNNING)

    def _execute_attempt(
        self,
        step: Step,
        attempt: Attempt,
        step_defination: str,
    ) -> ExecutionResult:

        try:
            return self.executor.execute(step, step_defination)

        except Exception as exc:
            return ExecutionResult(
                success=False,
                error=str(exc),
                error_code=type(exc).__name__,
            )
