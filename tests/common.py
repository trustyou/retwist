import twisted.internet.defer
import twisted.web.server
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
        return "/" + "/".join(self.postpath)


def _render(resource, request):
    """
    Simulate rendering of a Twisted resource.
    :param resource: Twisted Resource with render() method.
    :param request: Request (or mock object).
    :return: Deferred 
    """
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return twisted.internet.defer.succeed(None)
    elif result is twisted.web.server.NOT_DONE_YET:
        if request.finished:
            return twisted.internet.defer.succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))
