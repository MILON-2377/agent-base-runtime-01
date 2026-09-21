import random
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
    jitter_enabled: bool = False


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

        # Calculate delay for the next attempt.
        delay = self._calculate_delay(failure.attempt_number)

        # Retry is allowed.
        return RetryDecision(
            should_retry=True,
            delay_seconds=delay,
            reason="retryable_failure",
        )

    def _is_retryable(self, failure: FailureContext) -> bool:
        if not self.config.retryable_error_codes:
            return False

        if failure.error_code is None:
            return False

        return failure.error_code in self.config.retryable_error_codes

    def _calculate_delay(self, attempt_number: int) -> float:

        delay = self.config.base_delay_seconds * (2 ** (attempt_number - 1))

        delay = min(delay, self.config.max_delay_seconds)

        if self.config.jitter_enabled:
            delay = random.uniform(0, delay)

        return delay
