from runtime.retry_policy import (
    FailureContext,
    RetryPolicy,
    RetryPolicyConfig,
)


def test_retryable_failure_should_retry():
    config = RetryPolicyConfig(
        max_attempts=3,
        retryable_error_codes={"SERVICE_TIMEOUT"},
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=1,
        error_type="TimeoutError",
        error_code="SERVICE_TIMEOUT",
        error_message="API timeout",
        operation="search_hotels",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is True
    assert decision.reason == "retryable_failure"


def test_non_retryable_failure_should_not_retry():
    config = RetryPolicyConfig(
        max_attempts=3,
        retryable_error_codes={"SERVICE_TIMEOUT"},
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=1,
        error_type="ValidationError",
        error_code="INVALID_REQUEST",
        error_message="Invalid hotel query",
        operation="search_hotels",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is False
    assert decision.reason == "non_retryable_failure"


def test_max_attempts_should_stop_retry():
    config = RetryPolicyConfig(
        max_attempts=3,
        retryable_error_codes={"SERVICE_TIMEOUT"},
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=3,
        error_type="TimeoutError",
        error_code="SERVICE_TIMEOUT",
        error_message="API timeout",
        operation="search_hotels",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is False
    assert decision.reason == "max_attempts_reached"