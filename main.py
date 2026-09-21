from runtime.retry_policy import RetryPolicy, RetryPolicyConfig
from runtime.run import Run, RunStatus
from runtime.runtime import Runtime
from runtime.state_machine import RunStateMachine

state_machine = RunStateMachine()
runtime = Runtime(state_machine)


# -----------------------
# Valid transition
# -----------------------

run = Run(run_id="run-123")


print("Before valid transition:")
print("Status:", run.status)
print("History:", run.lifecycle_history)


success = runtime.transition(run, RunStatus.QUEUED)


print("\nAfter CREATED -> QUEUED")

print("Transition success", success)
print("Current status: ", run.status)
print("History: ", run.lifecycle_history)


# -------------------------
# Invalid transition
# -------------------------

invalid_run = Run(run_id="run-456")

print("\nBefore invalid transition:")
print("Status:", invalid_run.status)
print("History:", invalid_run.lifecycle_history)

success = runtime.transition(
    invalid_run,
    RunStatus.RUNNING,
)

print("\nAfter CREATED -> RUNNING:")
print("Success:", success)
print("Status:", invalid_run.status)
print("History:", invalid_run.lifecycle_history)
