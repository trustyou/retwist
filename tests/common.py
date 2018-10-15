from typing import Any, Union

from twisted.internet.defer import succeed
from twisted.web.http import Request
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.test.requesthelper import DummyRequest


class MyDummyRequest(DummyRequest):

    def notifyFinish(self):
        # Working around a possible bug in DummyRequest, where self._finishedDeferreds somehow gets set to None
        if self._finishedDeferreds is None:
            self._finishedDeferreds = []
        return DummyRequest.notifyFinish(self)

    @property
    def path(self):
        # "path" property is missing in DummyRequest for some reason
        return b"/" + b"/".join(self.postpath)


def _render(resource, request):
    # type: (Resource, Union[DummyRequest, Request]) -> Any
    """
    Simulate rendering of a Twisted resource.
    :param resource: Twisted Resource with render() method.
    :param request: Request (or mock object).
    :return: Deferred
    """
    result = resource.render(request)
    if isinstance(result, bytes):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result == NOT_DONE_YET:
        if request.finished:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))
