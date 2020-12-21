import logging
import os
from typing import Optional, Union

from twisted.python import log as twisted_log


def redirect_twisted_logging(logger_name=None, log_level=None):
    # type: (Optional[str], Optional[Union[int, str]]) -> None
    """
    Redirect Twisted's log messages to the Python logging module.

    Twisted has its own logging system (several, actually). Calling this method redirects all Twisted log messages to
    Python logging, by default as logger name "twisted", and for levels WARNING and up.

    :param logger_name: Name of the Twisted logger, so you can retrieve and configure it with `getLogger(...)`
    :param log_level: Log level for the messages to be forward. Default is WARNING
    """
    if logger_name is None:
        logger_name = "twisted"
    if log_level is None:
        log_level = logging.WARNING

    # Redirect messages from Twisted's log system to Python logging
    observer = twisted_log.PythonLoggingObserver(loggerName=logger_name)
    observer.start()

    # Adjust the log level, because debug and info messages are too verbose for most use cases
    logging.getLogger(logger_name).setLevel(log_level)

    # Twisted will by default print error messages to stderr until it has been instructed via `startLogging` to use a
    # different log handler. We silence Twisted's logging here, since we already redirect to Python's logging system.
    # There must be a better way to do this!
    twisted_log.startLogging(open(os.devnull, "w"))
