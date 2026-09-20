from .attempt import AttemptStatus


class AttemptStateMachine:
    ALLOWED_TRANSITIONS = {
        AttemptStatus.PENDING: {AttemptStatus.RUNNING},
        AttemptStatus.RUNNING: {
            AttemptStatus.SUCCEEDED,
            AttemptStatus.FAILED,
        },
    }

    def is_valid_transition(
        self, current_state: AttemptStatus, target_state: AttemptStatus
    ) -> bool:

        allowed_states = self.ALLOWED_TRANSITIONS.get(current_state, set())

        return target_state in allowed_states
