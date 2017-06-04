import json

import pytest
from twisted.internet import reactor, defer, task

import retwist
from tests.common import _render, MyDummyRequest


class EchoArgsPage(retwist.JsonResource):

    id = retwist.Param(required=True)
    show_details = retwist.BoolParam()

    def json_GET(self, request):
        return request.url_args


@pytest.inlineCallbacks
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


@pytest.inlineCallbacks
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



@pytest.inlineCallbacks
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
        _ = yield task.deferLater(reactor, 0.001, lambda: None)
        defer.returnValue("All working")


@pytest.inlineCallbacks
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


class BrokenPage(retwist.JsonResource):

    def __init__(self, *args, **kwargs):
        retwist.JsonResource.__init__(self, *args, **kwargs)
        self.failed = False

    @defer.inlineCallbacks
    def json_GET(self, request):
        _ = yield task.deferLater(reactor, 0.001, lambda: None / 0.0)
        defer.returnValue("Successfully divided by zero!")

    def log_server_error(self, failure, request):
        self.failed = True


@pytest.inlineCallbacks
def test_error_handling():
    """
    Check that exceptions in json_GET result in a 500 response code.
    """

    request = MyDummyRequest([b"/"])

    resource = BrokenPage()

    yield _render(resource, request)

    assert request.responseCode == 500
    assert resource.failed is True