try:
    from unittest.mock import Mock
except ImportError:
    # Python 3.2 and earlier
    from mock import Mock

import pytest
from twisted.python import log


def test_sentry():
    raven = pytest.importorskip("raven")

    # Import moved down here because it fails if raven isn't installed
    from retwist.util.sentry import enable_sentry_reporting

    mock_client = Mock(spec=raven.Client)
    enable_sentry_reporting(mock_client)

    log.err(IndexError("Oh noes!"))

    capture_exception_mock = mock_client.captureException  # type: Mock
    assert capture_exception_mock.called
