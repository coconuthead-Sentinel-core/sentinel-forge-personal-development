"""Unit tests for High-DPI awareness (lyceum.platform_dpi).

No GUI: the function only talks to the OS, so we assert its contract — it always
returns a non-empty status string and never raises, on any platform, and is safe
to call more than once (idempotent from the caller's perspective).
"""
import unittest

from lyceum.platform_dpi import enable_high_dpi_awareness


class PlatformDpiTest(unittest.TestCase):
    def test_returns_status_string(self):
        status = enable_high_dpi_awareness()
        self.assertIsInstance(status, str)
        self.assertTrue(status)

    def test_idempotent_no_raise(self):
        # Calling again must not raise even though awareness may already be set.
        enable_high_dpi_awareness()
        enable_high_dpi_awareness()


if __name__ == "__main__":
    unittest.main()
