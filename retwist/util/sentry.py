from typing import Any, Dict

import sentry_sdk
from twisted.python import log
from twisted.python.failure import Failure


def add_request_context_to_scope(context, scope):
    # type: (Dict[str, Any], sentry_sdk.Scope) -> None
    """
    Add context information which is useful for debugging from a Twisted request to a Sentry scope.
    """
    if "user_id" in context:
        scope.set_user({"id": context.pop("user_id", None)})

    scope.set_context("request", context)


def log_to_sentry(event):
    # type: (Dict[str, Any]) -> None
    """
    Twisted log observer for reporting errors to sentry.
    :param event: Twisted log event dictionary.
    """
    if not event.get("isError") or "failure" not in event:
        return

    failure = event["failure"]  # type: Failure
    exc = failure.value
    exc_tuple = (type(exc), exc, failure.getTracebackObject())

    if "context" in event:
        # If a Twisted request has been added as context to the logged event, we can extract useful debug info
        context = event["context"]  # type: Dict[str, Any]
        with sentry_sdk.push_scope() as scope:
            add_request_context_to_scope(context, scope)
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
