from .step import StepStatus


class StepStateMachine:
    ALLOWED_TRANSITIONS = {
        StepStatus.PENDING: {StepStatus.RUNNING, StepStatus.CANCELLED},
        StepStatus.RUNNING: {
            StepStatus.COMPLETED,
            StepStatus.FAILED,
            StepStatus.CANCELLED,
        },
    }

    def is_valid_transition(
        self,
        current_state: StepStatus,
        target_state: StepStatus,
    ) -> bool:

        allowed_states = self.ALLOWED_TRANSITIONS.get(current_state, set())

        return target_state in allowed_states
