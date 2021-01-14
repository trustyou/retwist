import json

import pytest_twisted
from twisted.internet import reactor, defer, task
from twisted.python import log
from twisted.python.failure import Failure
from twisted.web.server import NOT_DONE_YET

import retwist
from tests.common import _render, MyDummyRequest


class EchoArgsPage(retwist.JsonResource):

    id = retwist.Param(required=True)
    show_details = retwist.BoolParam()

    def json_GET(self, request):
        return request.url_args


@pytest_twisted.inlineCallbacks
def test_json_resource():
    """
    Test regular synchronous JSON rendering.
    """

    request = MyDummyRequest([b"/"])
    request.addArg(b"id", b"1234")
    request.addArg(b"show_details", b"false")

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = b"".join(request.written)
    response = json.loads(response_str.decode())

    assert response == {
        "id": "1234",
        "show_details": False,
    }


@pytest_twisted.inlineCallbacks
def test_param_error():
    """
    Test that errors during parsing parameters return a correct error document.
    """

    # Will produce error since required "id" is missing
    request = MyDummyRequest([b"/"])
    resource = EchoArgsPage()
    yield _render(resource, request)

    assert request.responseCode == 400
    response_str = b"".join(request.written)
    # Check that the error is valid JSON, that's all we want
    json.loads(response_str.decode())


@pytest_twisted.inlineCallbacks
def test_jsonp():

    # Check that response is wrapped in callback

    request = MyDummyRequest([b"/"])
    request.addArg(b"id", b"1234")
    request.addArg(b"callback", b"myCallback")

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = b"".join(request.written)
    assert response_str.startswith(b"myCallback(")
    assert response_str.endswith(b")")

    # Reject invalid callback

    request = MyDummyRequest(b"/")
    evil_callback = b"alert('hi');"
    request.addArg(b"id", b"1234")
    request.addArg(b"callback", evil_callback)

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = b"".join(request.written)
    assert evil_callback not in response_str
    assert request.responseCode == 400


class AsyncPage(retwist.JsonResource):

    @defer.inlineCallbacks
    def json_GET(self, request):
        yield task.deferLater(reactor, 0.001, lambda: None)
        defer.returnValue("All working")


@pytest_twisted.inlineCallbacks
def test_async_json_resource():
    """
    Make sure that asynchronous json_GET methods are supported.
    """

    request = MyDummyRequest([b"/"])

    resource = AsyncPage()

    yield _render(resource, request)

    response_str = b"".join(request.written)
    response = json.loads(response_str.decode())

    assert response == "All working"


# Errors can either happen synchronously, i.e. there is a current exception object in sys.exc_info. Or asynchronously,
# i.e. an errback gets called with a Failure. Let's test both possible code paths:


class SyncBrokenPage(retwist.JsonResource):

    def __init__(self):
        retwist.JsonResource.__init__(self)
        self.failed = False

    def json_GET(self, request):
        None / 0.0
        request.write(b"Successfully divided by zero!")
        return NOT_DONE_YET


class AsyncBrokenPage(retwist.JsonResource):

    def __init__(self):
        retwist.JsonResource.__init__(self)
        self.failed = False

    @defer.inlineCallbacks
    def json_GET(self, request):
        yield task.deferLater(reactor, 0.001, lambda: None / 0.0)
        defer.returnValue("Successfully divided by zero!")


@pytest_twisted.inlineCallbacks
def test_error_handling():
    """
    Check that exceptions in json_GET result in a 500 response code.
    """

    def err_observer(event):
        # type: (dict) -> None
        assert event["isError"]
        failure = event["failure"]
        assert isinstance(failure, Failure)
        exception = failure.value
        assert isinstance(exception, TypeError)
        assert event["context"] == {
            'data': {},
            'headers': {},
            'method': b'GET',
            'query_string': b'http:dummy/',
            'url': b'http://dummy/'
        }
        err_observer.called = True

    log.addObserver(err_observer)

    for resource in [SyncBrokenPage(), AsyncBrokenPage()]:
        request = MyDummyRequest([b"/"])
        err_observer.called = False
        yield _render(resource, request)

        assert request.responseCode == 500
        assert err_observer.called is True, "Error handler not called for {}".format(type(resource).__name__)

    log.removeObserver(err_observer)
