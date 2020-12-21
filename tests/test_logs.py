import logging

from twisted.python import log as twisted_log

from retwist.util.logs import redirect_twisted_logging


def test_redirect_twisted_logging():

    # Assemble logging config and handlers ...

    logged_records = []

    class MockHandler(logging.Handler):
        def emit(self, record):
            # type: (logging.LogRecord) -> None
            logged_records.append(record)

    logger_name = "test_redirect_twisted_logging"
    redirect_twisted_logging(logger_name, logging.DEBUG)

    mock_handler = MockHandler()
    logging.getLogger(logger_name).addHandler(mock_handler)

    # Log a test message

    log_msg = "See you on the other side"
    twisted_log.msg(log_msg)

    # Assert that this message was captured by the mock handler

    assert any(
        (record.name == logger_name and (log_msg in record.message))
        for record in logged_records
    )
