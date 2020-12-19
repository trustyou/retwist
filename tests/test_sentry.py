try:
    from unittest.mock import Mock
except ImportError:
    # Python 3.2 and earlier
    from mock import Mock

import pytest
from twisted.python import log


def test_sentry(monkeypatch):
    sentry_sdk = pytest.importorskip("sentry_sdk")

    mock_capture_exception = Mock(spec=sentry_sdk.capture_exception)
    monkeypatch.setattr(sentry_sdk, "capture_exception", mock_capture_exception)

    # Import moved down here because it fails if sentry-sdk isn't installed
    from retwist.util.sentry import enable_sentry_reporting

    enable_sentry_reporting()

    log.err(IndexError("Oh noes!"))

    assert mock_capture_exception.called
