try:
    from unittest.mock import Mock
except ImportError:
    # Python 3.2 and earlier
    from mock import Mock

import pytest
from twisted.web.http_headers import Headers

from retwist.json_resource import JsonResource
from .common import MyDummyRequest


class DummyResource(JsonResource):

    def json_GET(self, request):
        raise IndexError("Oh noes!")


@pytest.fixture
def mock_capture_exception(monkeypatch):
    sentry_sdk = pytest.importorskip("sentry_sdk")
    mock_capture_exception = Mock(spec=sentry_sdk.capture_exception)
    monkeypatch.setattr(sentry_sdk, "capture_exception", mock_capture_exception)
    return mock_capture_exception


def test_sentry(mock_capture_exception):
    # Import moved down here because it fails if sentry-sdk isn't installed
    from retwist.util.sentry import enable_sentry_reporting
    enable_sentry_reporting()

    request = MyDummyRequest([b"the", b"path"])
    request.args = {
        b"id": b"1234"
    }
    request.requestHeaders = Headers({b"Content-Type": [b"text/plain"]})
    resource = DummyResource()

    resource.render(request)

    assert mock_capture_exception.called
