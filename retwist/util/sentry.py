import sentry_sdk
from twisted.python.failure import Failure
from twisted.python import log


def log_to_sentry(event):
    # type: (dict) -> None
    """
    Twisted log observer for reporting errors to sentry.
    :param event: Twisted log event dictionary.
    """
    if not event.get("isError") or "failure" not in event:
        return

    f = event["failure"]  # type: Failure
    sentry_sdk.capture_exception(f.value)


def enable_sentry_reporting():
    # type: () -> None
    """
    Enable Sentry logging for any errors reported via twisted.python.log.err.

    Call sentry_sdk.init() before this.
    """
    log.addObserver(log_to_sentry)
