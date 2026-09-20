from dataclasses import dataclass


@dataclass
class FailureContext:
    attempt_number: int
    error_type: str
    error_code: str | None = None
    error_message: str | None = None
    operation: str | None = None


@dataclass
class RetryPolicyConfig:
    max_attempts: int = 3
    retryable_error_codes: set[str] | None = None
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0


@dataclass
class RetryDecision:
    should_retry: bool
    delay_seconds: float = 0.0
    reason: str = ""


class RetryPolicy:
    def __init__(self, config: RetryPolicyConfig):
        self.config = config

    def decide(self, failure: FailureContext) -> RetryDecision:
        # 1. Is the failure retryable?
        if not self._is_retryable(failure):
            return RetryDecision(
                should_retry=False,
                reason="non_retryable_failure",
            )

        # 2. Are attempts remaining?
        if failure.attempt_number >= self.config.max_attempts:
            return RetryDecision(
                should_retry=False,
                reason="max_attempts_reached",
            )

        # Retry is allowed.
        return RetryDecision(
            should_retry=True,
            reason="retryable_failure",
        )

    def _is_retryable(self, failure: FailureContext) -> bool:
        if self.config.retryable_error_codes is None:
            return False

        if failure.error_code is None:
            return False

        return failure.error_code in self.config.retryable_error_codes
