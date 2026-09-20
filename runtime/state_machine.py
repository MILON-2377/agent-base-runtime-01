from .run import RunStatus


class RunStateMachine:
    ALLOWED_TRANSITIONS = {
        RunStatus.CREATED: {RunStatus.QUEUED},
        RunStatus.QUEUED: {RunStatus.RUNNING},
        RunStatus.RUNNING: {
            RunStatus.PAUSED,
            RunStatus.COMPLETED,
            RunStatus.FAILED,
            RunStatus.CANCELLED,
            RunStatus.TIMEOUT,
        },
        RunStatus.PAUSED: {
            RunStatus.RUNNING,
        },
    }

    def is_valid_transition(
        self, current_status: RunStatus, target_state: RunStatus
    ) -> bool:

        allowed_status = self.ALLOWED_TRANSITIONS.get(current_status, set())

        return target_state in allowed_status
