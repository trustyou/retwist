import json

import pytest
from twisted.internet import reactor, defer, task

import retwist
from tests.common import _render, MyDummyRequest


class EchoArgsPage(retwist.JsonResource):

    id = retwist.Param(required=True)
    show_details = retwist.BoolParam()

    def json_GET(self, request):
        return self.parse_args(request)


@pytest.inlineCallbacks
def test_json_resource():
    """
    Test regular synchronous JSON rendering.
    """

    request = MyDummyRequest("/")
    request.addArg("id", "1234")
    request.addArg("show_details", "false")

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = "".join(request.written)
    response = json.loads(response_str)

    assert response == {
        "id": "1234",
        "show_details": False,
    }


@pytest.inlineCallbacks
def test_jsonp():

    # Check that response is wrapped in callback

    request = MyDummyRequest("/")
    request.addArg("id", "1234")
    request.addArg("callback", "myCallback")

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = "".join(request.written)
    assert response_str.startswith("myCallback(")
    assert response_str.endswith(")")

    # Reject invalid callback

    request = MyDummyRequest("/")
    evil_callback = "alert('hi');"
    request.addArg("callback", evil_callback)

    resource = EchoArgsPage()

    yield _render(resource, request)

    response_str = "".join(request.written)
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

    request = MyDummyRequest("/")

    resource = AsyncPage()

    yield _render(resource, request)

    response_str = "".join(request.written)
    response = json.loads(response_str)

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

    request = MyDummyRequest("/")

    resource = BrokenPage()

    yield _render(resource, request)

    assert request.responseCode == 500
    assert resource.failed is True