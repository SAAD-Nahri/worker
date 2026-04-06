from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, TypeVar


T = TypeVar("T")

RETRYABLE_HTTP_STATUS_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})


@dataclass(frozen=True)
class TransportRetryPolicy:
    max_attempts: int = 1
    initial_delay_seconds: float = 0.0
    backoff_multiplier: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts <= 0:
            raise ValueError("Transport retry policy max_attempts must be greater than zero.")
        if self.initial_delay_seconds < 0:
            raise ValueError("Transport retry policy initial_delay_seconds cannot be negative.")
        if self.backoff_multiplier < 1:
            raise ValueError("Transport retry policy backoff_multiplier must be at least 1.")


def execute_with_retry(
    operation: Callable[[], T],
    policy: TransportRetryPolicy,
    *,
    is_retryable_error: Callable[[BaseException], bool],
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[T, int]:
    attempts = 0
    current_delay = policy.initial_delay_seconds
    while True:
        attempts += 1
        try:
            return operation(), attempts
        except BaseException as exc:
            if attempts >= policy.max_attempts or not is_retryable_error(exc):
                raise
            if current_delay > 0:
                sleeper(current_delay)
            current_delay *= policy.backoff_multiplier


def is_retryable_transport_error(exc: BaseException) -> bool:
    retryable_flag = getattr(exc, "retryable", None)
    if retryable_flag is True:
        return retryable_flag

    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int) and status_code in RETRYABLE_HTTP_STATUS_CODES:
        return True

    message = str(exc).lower()
    retryable_markers = (
        "timed out",
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "connection aborted",
        "connection refused",
        "request failed",
        "network is unreachable",
        "remote end closed connection",
    )
    if any(marker in message for marker in retryable_markers):
        return True
    return any(f"http {code}" in message for code in RETRYABLE_HTTP_STATUS_CODES)
