import sentry_sdk
from twisted.python import log
from twisted.python.failure import Failure
from twisted.web.http import Request


def add_request_context_to_scope(request, scope):
    # type: (Request, sentry_sdk.Scope) -> None
    """
    Add context information which is useful for debugging from a Twisted request to a Sentry scope.
    """
    scope.set_extra("url", request.uri)
    scope.set_extra("method", request.method)
    scope.set_extra("headers", request.getAllHeaders())
    scope.set_extra("query_string", request.uri.replace(request.path, b"").strip(b"?"))
    scope.set_extra("data", request.args)


def log_to_sentry(event):
    # type: (dict) -> None
    """
    Twisted log observer for reporting errors to sentry.
    :param event: Twisted log event dictionary.
    """
    if not event.get("isError") or "failure" not in event:
        return

    f = event["failure"]  # type: Failure
    exc = f.value

    if "request" in event:
        # If a Twisted request has been added as context to the logged event, we can extract useful debug info
        request = event["request"]  # type: Request
        with sentry_sdk.push_scope() as scope:
            add_request_context_to_scope(request, scope)
            sentry_sdk.capture_exception(exc)
    else:
        sentry_sdk.capture_exception(exc)


def enable_sentry_reporting():
    # type: () -> None
    """
    Enable Sentry logging for any errors reported via twisted.python.log.err.

    Call sentry_sdk.init() before this.
    """
    log.addObserver(log_to_sentry)
