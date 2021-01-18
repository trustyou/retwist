import inspect
from typing import Any, Dict

from twisted.web.error import Error
from twisted.web.http import Request
from twisted.web.resource import Resource

from retwist.param import BaseParam


class ParamResource(Resource):
    """
    Twisted resource with convenient parsing of parameters.

    Parameters are defined at class level:

    age = retwist.Param()

    You can then retrieve parameters by calling parse_args(request) in your render_* method.
    """

    ERROR_MSG = b"Error in parameter %s: %s"

    def parse_args(self, request):
        # type: (Request) -> Dict[str, Any]
        """
        Parse arguments from request. Throws twisted.web.error.Error instances on client errors.

        :param request: Twisted request
        :return: Dictionary of parameter names to parsed values
        """
        args = {}
        for name, param in inspect.getmembers(self, lambda member: isinstance(member, BaseParam)):

            # Name can be overridden. This is useful if parameter name is a Python reserved keyword
            if param.name is not None:
                name = param.name

            try:
                val = param.parse_from_request(name, request)
            except Error as ex:
                error_msg = ParamResource.ERROR_MSG % (name.encode(), ex.message)
                raise Error(ex.status, error_msg)
            else:
                args[name] = val
        return args
