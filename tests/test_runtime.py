from runtime.attempt import Attempt, AttemptStatus
from runtime.attempt_state_machine import AttemptStateMachine
from runtime.execution import ExecutionResult
from runtime.executor import Executor
from runtime.run import Run, RunStatus
from runtime.runtime import Runtime
from runtime.state_machine import RunStateMachine
from runtime.step import Step, StepStatus
from runtime.step_state_machine import StepStateMachine


class MockExecutor(Executor):
    def execute(self, step: Step, step_defination: str) -> ExecutionResult:
        return ExecutionResult(success=True, output=f"Executed: {step_defination}")


class FailingMockExecutor(Executor):
    def execute(self, step: Step, step_defination: str) -> ExecutionResult:
        return ExecutionResult(success=False, error="API timeout")


run_state_machine = RunStateMachine()
step_state_machine = StepStateMachine()
attempt_state_machine = AttemptStateMachine()
executor = MockExecutor()


runtime = Runtime(
    run_state_machine,
    step_state_machine,
    attempt_state_machine=attempt_state_machine,
    executor=executor,
)

run = Run(run_id="run-123")


# def test_valid_transition_updates_status_and_history():

#     success = runtime.transition_run(run, RunStatus.QUEUED)

#     assert success is True
#     assert run.status == RunStatus.QUEUED
#     assert run.lifecycle_history == [RunStatus.CREATED, RunStatus.QUEUED]


# def test_invalid_transition_does_not_mutate_run():

#     success = runtime.transition_run(run, RunStatus.RUNNING)

#     assert success is False
#     assert run.status == RunStatus.CREATED
#     assert run.lifecycle_history == [RunStatus.CREATED]


# def test_full_lifecycle_with_pause_and_resume():

#     t1 = runtime.transition_run(run, RunStatus.QUEUED)

#     t2 = runtime.transition_run(
#         run,
#         RunStatus.RUNNING,
#     )

#     t3 = runtime.transition_run(run, RunStatus.PAUSED)

#     t4 = runtime.transition_run(run, RunStatus.RUNNING)

#     t5 = runtime.transition_run(run, RunStatus.COMPLETED)

#     assert t1 is True
#     assert t2 is True
#     assert t3 is True
#     assert t4 is True
#     assert t5 is True

#     assert run.status == RunStatus.COMPLETED

#     assert run.lifecycle_history == [
#         RunStatus.CREATED,
#         RunStatus.QUEUED,
#         RunStatus.RUNNING,
#         RunStatus.PAUSED,
#         RunStatus.RUNNING,
#         RunStatus.COMPLETED,
#     ]


# def test_terminal_state_cannot_transition():

#     t1 = runtime.transition_run(run, RunStatus.QUEUED)

#     t2 = runtime.transition_run(run, RunStatus.RUNNING)

#     t3 = runtime.transition_run(run, RunStatus.COMPLETED)

#     invalid_t4 = runtime.transition_run(run, RunStatus.RUNNING)

#     assert t1 is True
#     assert t2 is True
#     assert t3 is True
#     assert invalid_t4 is False

#     assert run.status == RunStatus.COMPLETED

#     assert run.lifecycle_history == [
#         RunStatus.CREATED,
#         RunStatus.QUEUED,
#         RunStatus.RUNNING,
#         RunStatus.COMPLETED,
#     ]


def test_valid_pending_to_running_step_transition():

    step = Step(
        step_id="step-123",
        run_id=run.run_id,
    )

    s_t1 = runtime.transition_step(step, StepStatus.RUNNING)

    assert s_t1 is True

    assert step.status == StepStatus.RUNNING

    assert step.lifecycle_history == [
        StepStatus.PENDING,
        StepStatus.RUNNING,
    ]


def test_valid_pending_to_cancelled_step_transition():

    step = Step(step_id="step-456", run_id=run.run_id)

    result = runtime.transition_step(step, StepStatus.CANCELLED)

    assert result is True

    assert step.status == StepStatus.CANCELLED

    assert step.lifecycle_history == [StepStatus.PENDING, StepStatus.CANCELLED]


def test_execute_step_successfully():

    step = Step(step_id="step-123", run_id=run.run_id)

    result = runtime.execute_step(step, "search hotels")

    assert result.success is True
    assert result.output == "Executed: search hotels"

    assert step.status == StepStatus.COMPLETED

    assert step.lifecycle_history == [
        StepStatus.PENDING,
        StepStatus.RUNNING,
        StepStatus.COMPLETED,
    ]


def test_execute_step_failure():

    executor = FailingMockExecutor()

    runtime = Runtime(
        state_machine=RunStateMachine(),
        step_state_machine=StepStateMachine(),
        executor=executor,
    )

    step = Step(step_id="step-123", run_id="run-123")

    result = runtime.execute_step(step, "search hotels")

    assert result.success is False

    assert result.error == "API timeout"

    assert step.status == StepStatus.FAILED

    assert step.lifecycle_history == [
        StepStatus.PENDING,
        StepStatus.RUNNING,
        StepStatus.FAILED,
    ]


def test_attempt_starts_as_pending():

    attempt = Attempt(attempt_id="attempt-001", step_id="step-001")

    assert attempt.status == AttemptStatus.PENDING
    assert attempt.lifecycle_history == [AttemptStatus.PENDING]


def test_attempt_valid_transition():

    state_machine = AttemptStateMachine()

    assert state_machine.is_valid_transition(
        AttemptStatus.PENDING, AttemptStatus.RUNNING
    )

    assert state_machine.is_valid_transition(
        AttemptStatus.RUNNING, AttemptStatus.SUCCEEDED
    )

    assert state_machine.is_valid_transition(
        AttemptStatus.RUNNING, AttemptStatus.FAILED
    )


def test_attempt_ternimal_states_cannot_restart():

    state_machine = AttemptStateMachine()

    assert not state_machine.is_valid_transition(
        AttemptStatus.FAILED, AttemptStatus.RUNNING
    )

    assert not state_machine.is_valid_transition(
        AttemptStatus.SUCCEEDED, AttemptStatus.RUNNING
    )


def test_step_starts_with_no_attempts():

    step = Step(step_id="step-001", run_id="run-001")

    assert step.attempts == []


def test_steps_have_indepent_attempt_lists():

    step_a = Step(step_id="step-001", run_id="run-001")

    step_b = Step(step_id="step-002", run_id="run-001")

    attempt = Attempt(attempt_id="attempt-001", step_id="step-001")

    step_a.attempts.append(attempt)

    assert len(step_a.attempts) == 1

    assert len(step_b.attempts) == 0


def test_runtime_creates_running_attempt():

    executor = MockExecutor()

    runtime = Runtime(
        state_machine=RunStateMachine(),
        step_state_machine=StepStateMachine(),
        attempt_state_machine=AttemptStateMachine(),
        executor=executor,
    )

    step = Step(step_id="step-123", run_id="run-123")

    runtime.execute_step(step, "search hotels")

    assert len(step.attempts) == 1

    attempt = step.attempts[0]

    assert attempt.step_id == "step-123"
    assert attempt.status == AttemptStatus.RUNNING
    assert attempt.lifecycle_history == [AttemptStatus.PENDING, AttemptStatus.RUNNING]

    assert step.status == StepStatus.RUNNING


def test_runtime_transitions_attempt():
    runtime = Runtime(
        state_machine=RunStateMachine(),
        step_state_machine=StepStateMachine(),
        attempt_state_machine=AttemptStateMachine(),
        executor=MockExecutor(),
    )

    attempt = Attempt(
        attempt_id="attempt-001",
        step_id="step-001",
    )

    assert runtime.transition_attempt(
        attempt,
        AttemptStatus.RUNNING,
    )

    assert attempt.status == AttemptStatus.RUNNING

    assert runtime.transition_attempt(
        attempt,
        AttemptStatus.SUCCEEDED,
    )

    assert attempt.status == AttemptStatus.SUCCEEDED

    assert attempt.lifecycle_history == [
        AttemptStatus.PENDING,
        AttemptStatus.RUNNING,
        AttemptStatus.SUCCEEDED,
    ]


def test_runtime_rejects_invalid_attempt_transition():
    runtime = Runtime(
        state_machine=RunStateMachine(),
        step_state_machine=StepStateMachine(),
        attempt_state_machine=AttemptStateMachine(),
        executor=MockExecutor(),
    )

    attempt = Attempt(
        attempt_id="attempt-001",
        step_id="step-001",
    )

    runtime.transition_attempt(
        attempt,
        AttemptStatus.RUNNING,
    )

    runtime.transition_attempt(
        attempt,
        AttemptStatus.SUCCEEDED,
    )

    assert not runtime.transition_attempt(
        attempt,
        AttemptStatus.RUNNING,
    )

    assert attempt.status == AttemptStatus.SUCCEEDED

    assert attempt.lifecycle_history == [
        AttemptStatus.PENDING,
        AttemptStatus.RUNNING,
        AttemptStatus.SUCCEEDED,
    ]


class ExceptionMockExecutor(Executor):
    def execute(self, step: Step, step_defination: str) -> ExecutionResult:
        raise TimeoutError("API timeout")


def test_executor_exception_marks_attempt_and_step_failed():

    executor = ExceptionMockExecutor()

    runtime = Runtime(
        state_machine=RunStateMachine(),
        step_state_machine=StepStateMachine(),
        attempt_state_machine=AttemptStateMachine(),
        executor=executor,
    )

    step = Step(step_id="step-123", run_id="run-123")

    result = runtime.execute_step(step, "search hotels")

    assert result.success is False
    assert result.error == "API timeout"

    assert step.status == StepStatus.FAILED

    attempt = step.attempts[0]

    assert attempt.status == AttemptStatus.FAILED

    assert attempt.lifecycle_history == [
        AttemptStatus.PENDING,
        AttemptStatus.RUNNING,
        AttemptStatus.FAILED,
    ]
