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


def test_first_retry_uses_base_delay():

    config = RetryPolicyConfig(
        max_attempts=3,
        retryable_error_codes={"SERVICE_TIMEOUT"},
        base_delay_seconds=2.0,
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=1,
        error_type="TimeoutError",
        error_code="SERVICE_TIMEOUT",
        operation="search_hotels",
        error_message="api timeout",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is True
    assert decision.delay_seconds == 2.0


def test_exponential_backoff_increases_delay():
    config = RetryPolicyConfig(
        max_attempts=5,
        retryable_error_codes={"SERVICE_TIMEOUT"},
        base_delay_seconds=2.0,
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=3,
        error_type="TimeoutError",
        error_code="SERVICE_TIMEOUT",
        error_message="API service timeout",
        operation="search_hotels",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is True
    assert decision.delay_seconds == 8.0


def test_delay_is_capped_by_max_delay():
    config = RetryPolicyConfig(
        max_attempts=10,
        retryable_error_codes={"SERVICE_TIMEOUT"},
        base_delay_seconds=2.0,
        max_delay_seconds=5.0,
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=5,
        error_type="TimeoutError",
        error_code="SERVICE_TIMEOUT",
        error_message="API service timeout",
        operation="search_hotels",
    )

    decision = policy.decide(failure)

    assert decision.should_retry is True
    assert decision.delay_seconds == 5.0


def test_jitter_keeps_delay_within_calculated_range():

    config = RetryPolicyConfig(
        max_attempts=5,
        retryable_error_codes={"SERVICE_TIMEOUT"},
        base_delay_seconds=2.0,
        max_delay_seconds=30.0,
        jitter_enabled=True,
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

    assert decision.should_retry is True
    assert 0.0 <= decision.delay_seconds <= 8.0



def test_missing_error_code_is_not_retryable():
    config = RetryPolicyConfig(
        max_attempts=3,
        retryable_error_codes={"SERVICE_TIMEOUT"},
    )

    policy = RetryPolicy(config)

    failure = FailureContext(
        attempt_number=1,
        error_type="TimeoutError",
        error_code=None,
    )

    decision = policy.decide(failure)

    assert decision.should_retry is False
    assert decision.reason == "non_retryable_failure"