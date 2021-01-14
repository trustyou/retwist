from typing import Dict

import sentry_sdk
from twisted.python import log
from twisted.python.failure import Failure
from twisted.web.http import Request


def add_request_context_to_scope(request, scope, context):
    # type: (Request, sentry_sdk.Scope, Dict) -> None
    """
    Add error context information which is useful for debugging from a Twisted request to a Sentry scope.
    """
    request_context = {
        "url": request.uri,
        "method": request.method,
        "headers": request.getAllHeaders(),
        "query_string": request.uri.replace(request.path, b"").strip(b"?"),
        "data": request.args
    }

    if "user_id" in context:
        scope.set_user({"id": context.pop("user_id", None)})

    request_context.update(context)
    scope.set_context("request", request_context)


def log_to_sentry(event):
    # type: (dict) -> None
    """
    Twisted log observer for reporting errors to sentry.
    :param event: Twisted log event dictionary.
    """
    if not event.get("isError") or "failure" not in event:
        return

    failure = event["failure"]  # type: Failure
    exc = failure.value
    exc_tuple = (type(exc), exc, failure.getTracebackObject())

    if all(key in event for key in ["request", "context"]):
        # If a Twisted request has been added as context to the logged event, we can extract useful debug info
        request = event["request"]  # type: Request
        context = event["context"]  # type: Dict
        with sentry_sdk.push_scope() as scope:
            add_request_context_to_scope(request, scope, context)
            sentry_sdk.capture_exception(exc_tuple)
    else:
        sentry_sdk.capture_exception(exc_tuple)


def enable_sentry_reporting():
    # type: () -> None
    """
    Enable Sentry logging for any errors reported via twisted.python.log.err.

    Call sentry_sdk.init() before this.
    """
    log.addObserver(log_to_sentry)
