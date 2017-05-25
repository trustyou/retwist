import json
import logging
import re
import traceback

import twisted.internet.defer
import twisted.internet.error
import twisted.python.failure
import twisted.web.error
import twisted.web.resource
import twisted.web.server

import retwist.param_resource


class JsonResource(retwist.param_resource.ParamResource):
    """
    Twisted resource with convenience methods to encode JSON responses. Supports JSONP.
    """

    encoding = "utf-8"

    jsonp_callback_re = re.compile("^[_a-zA-Z0-9\.$]+$")

    @classmethod
    def json_dump_default(cls, o):
        """
        Override this to implement custom JSON encoding. Passed to json.dump method.
        :param o: Object which cannot be JSON-serialized.
        :return: JSON-serializable object (or throw TypeError)
        """

        raise TypeError()

    def json_GET(self, request):
        """
        Override this to return JSON data to render.
        
        :param request: Twisted request.
        """

        raise NotImplementedError()

    def render_GET(self, request):
        """
        Get JSON data from json_GET, and render for the client.
        
        Do not override in sub classes ...
        :param request: Twisted request
        """

        json_def = twisted.internet.defer.maybeDeferred(self.json_GET, request)
        json_def.addCallback(self.send_json_response, request)
        json_def.addErrback(self.send_failure, request)

        # handle connection failures
        request.notifyFinish().addErrback(self.on_connection_closed, json_def)

        return twisted.web.server.NOT_DONE_YET

    def response_envelope(self, response, status_code=200, status_message=None):
        """
        Implement this to transform JSON responses before sending, e.g. by putting HTTP status codes in the response.
        
        :param response: JSON data about to be sent to client 
        :param status_code: HTTP status code
        :param status_message: Optional status message, e.g. error message
        :return: Wrapped JSON-serializable data
        """

        return response

    def send_json_response(self, response, request, status_code=200, status_message=None):
        """
        Send JSON data to client.
        
        :param response: JSON-serializable data 
        :param request: Twisted request
        :param status_code: HTTP status code
        :param status_message: Optional status message, e.g. error message
        """

        is_jsonp = len(request.args.get("callback", [])) == 1
        if is_jsonp:
            callback = request.args["callback"][0]
            if not self.jsonp_callback_re.match(callback):
                del request.args["callback"]
                return self.send_json_response("Invalid callback", request, status_code=400)
            request.setHeader("Content-Type", "application/javascript; charset=utf-8")
            request.write(callback + "(")
        else:
            request.setHeader("Content-Type", "application/json; charset=utf-8")
            request.setResponseCode(status_code)

        response = self.response_envelope(response, status_code=status_code, status_message=status_message)
        json.dump(response, request, allow_nan=False, default=self.json_dump_default)

        if is_jsonp:
            request.write(")")

        request.finish()

    def log_server_error(self, failure, request):
        """
        Oh no, a server error happened! Log it. The request is just passed for inspection; don't modify it.
        
        :param failure: Twisted failure instance, wrapping an exception 
        :param request: Twisted request
        :return: 
        """

        error_msg = failure.getErrorMessage()
        exception = failure.value
        tb = failure.getTracebackObject()
        tb_list = traceback.extract_tb(tb)
        tb_formatted = traceback.format_list(tb_list)
        tb_str = "".join(tb_formatted)
        logging.error("%s (%s) @ %s\n%s", type(exception).__name__, error_msg, request.uri, tb_str)

    def send_failure(self, failure, request):
        """
        Send an error to the client. For connection errors, we do nothing - no chance to send anything. For client
        errors, we show an informative error message. For server errors, we show a generic message, and log the error.
        
        :param failure: Twisted failure
        :param request: Twisted request
        """

        # This happens if the client closed the connection, or something similar.
        if failure.check(
            twisted.internet.defer.CancelledError,
            twisted.internet.error.ConnectionLost,
            twisted.internet.error.ConnectionDone,
            twisted.internet.error.ConnectError,
        ):
            return

        exception = failure.value
        error_msg = failure.getErrorMessage()

        # Client error
        if failure.check(twisted.web.error.Error):
            status_code = int(exception.status)
            if 400 <= status_code < 500:
                return self.send_json_response(error_msg, request, status_code=status_code)

        # Server error
        self.log_server_error(failure, request)
        return self.send_json_response("Server-side error", request, status_code=500)

    def on_connection_closed(self, failure, deferred):
        """
        Handle connection errors.
        
        :param failure: Twisted failure 
        :param deferred: The async call to json_GET
        """

        deferred.cancel()
