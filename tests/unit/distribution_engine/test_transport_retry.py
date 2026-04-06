from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from distribution_engine.transport_retry import (
    TransportRetryPolicy,
    execute_with_retry,
    is_retryable_transport_error,
)


class TransportRetryTests(unittest.TestCase):
    def test_execute_with_retry_retries_retryable_error(self) -> None:
        attempts = {"count": 0}

        class RetryableError(RuntimeError):
            retryable = True

        def _operation():
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RetryableError("temporary timeout")
            return "ok"

        value, used_attempts = execute_with_retry(
            _operation,
            TransportRetryPolicy(max_attempts=2, initial_delay_seconds=0.0),
            is_retryable_error=is_retryable_transport_error,
            sleeper=lambda _delay: None,
        )

        self.assertEqual(value, "ok")
        self.assertEqual(used_attempts, 2)

    def test_execute_with_retry_does_not_retry_non_retryable_error(self) -> None:
        attempts = {"count": 0}

        def _operation():
            attempts["count"] += 1
            raise RuntimeError("bad request")

        with self.assertRaisesRegex(RuntimeError, "bad request"):
            execute_with_retry(
                _operation,
                TransportRetryPolicy(max_attempts=3, initial_delay_seconds=0.0),
                is_retryable_error=is_retryable_transport_error,
                sleeper=lambda _delay: None,
            )

        self.assertEqual(attempts["count"], 1)


if __name__ == "__main__":
    unittest.main()
