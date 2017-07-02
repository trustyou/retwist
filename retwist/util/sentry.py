from raven import Client
from twisted.python import log


raven_client = None  # type: Client


def log_to_sentry(event):
    # type: (dict) -> None
    """
    Twisted log observer for reporting errors to sentry.
    :param event: Twisted log event dictionary.
    """
    if not event.get("isError") or "failure" not in event:
        return

    f = event["failure"]
    raven_client.captureException((f.type, f.value, f.getTracebackObject()))


def enable_sentry_reporting(client):
    # type: (Client) -> None
    """
    Enable Sentry logging for any errors reported via twisted.python.log.err.
    :param client: Already configured raven.Client
    """
    global raven_client
    raven_client = client
    log.addObserver(log_to_sentry)
