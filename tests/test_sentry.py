try:
    from unittest.mock import Mock, patch, call
except ImportError:
    # Python 3.2 and earlier
    from mock import Mock, patch, call

import pytest
from twisted.web.http_headers import Headers

from retwist.json_resource import JsonResource
from .common import MyDummyRequest


class DummyResource(JsonResource):

    def json_GET(self, request):
        raise IndexError("Oh noes!")


@pytest.fixture()
def sentry_sdk():
    return pytest.importorskip("sentry_sdk")


@pytest.fixture
def mock_capture_exception(sentry_sdk, monkeypatch):
    mock_capture_exception = Mock(spec=sentry_sdk.capture_exception)
    monkeypatch.setattr(sentry_sdk, "capture_exception", mock_capture_exception)
    return mock_capture_exception


@pytest.fixture
def dummy_request():
    request = MyDummyRequest([b"the", b"path"])
    request.args = {
        b"id": b"1234"
    }
    request.requestHeaders = Headers({b"Content-Type": [b"text/plain"]})
    return request


@pytest.fixture
def dummy_resource():
    return DummyResource()


@pytest.fixture
def dummy_request_context():
    return {
        'data': {b'id': b'1234'},
        'method': b'GET',
        'headers': {b'content-type': b'text/plain'},
        'url': b'http://dummy/',
        'query_string': b'http://dummy/'
    }


def test_sentry(mock_capture_exception, dummy_request, dummy_resource):
    # Import moved down here because it fails if sentry-sdk isn't installed
    from retwist.util.sentry import enable_sentry_reporting
    enable_sentry_reporting()

    from retwist.util.sentry import add_request_context_to_scope
    with patch("retwist.util.sentry.add_request_context_to_scope",
               wraps=add_request_context_to_scope) as mock_add_request_context_to_scope:
        dummy_resource.render(dummy_request)

        assert mock_capture_exception.called
        assert mock_add_request_context_to_scope.called


@pytest.mark.parametrize(
    "context,expected_user_id,expected_custom_context",
    [
        (
            {'test_key': 'test_data'},
            None,
            {'test_key': 'test_data'}
        ),
        (
            {'user_id': 'test_user_id'},
            "test_user_id",
            {}
        )
    ]
)
def test_add_request_context_to_scope(context, expected_user_id, expected_custom_context,
                                      dummy_request_context, sentry_sdk):
    from retwist.util.sentry import add_request_context_to_scope

    scope = Mock(spec=sentry_sdk.scope.Scope)
    request_context = dummy_request_context.copy()
    expected_context = dummy_request_context.copy()
    if context:
        request_context.update(context)
    if expected_custom_context:
        expected_context.update(expected_custom_context)
    expected_set_user_calls = [call({"id": expected_user_id})] if expected_user_id else []
    expected_set_context_calls = [call("request", expected_context)]

    add_request_context_to_scope(request_context, scope)

    assert scope.set_user.mock_calls == expected_set_user_calls
    assert scope.set_context.mock_calls == expected_set_context_calls
