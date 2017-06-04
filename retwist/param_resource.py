import inspect
from typing import Any, Dict

import twisted.web.http
import twisted.web.resource

import retwist.param


class ParamResource(twisted.web.resource.Resource):
    """
    Twisted resource with convenient parsing of parameters.
    
    Parameters are defined at class level:
    
    age = retwist.Param()
    
    You can then retrieve parameters by calling parse_args(request) in your render_* method.
    """

    def parse_args(self, request):
        # type: (twisted.web.http.Request) -> Dict[str, Any]
        """
        Parse arguments from request. Throws twisted.web.error.Error instances on client errors.
        
        :param request: Twisted request 
        :return: Dictionary of parameter names to parsed values
        """
        return {
            name: param.parse_from_request(name, request)
            for name, param in inspect.getmembers(self)
            if isinstance(param, retwist.Param)
        }