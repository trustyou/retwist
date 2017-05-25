import inspect

import twisted.web.resource

import retwist.param


class ParamResource(twisted.web.resource.Resource):
    """
    Twisted resource with convenient parsing of parameters.
    
    Parameters are defined at class level:
    
    age = retwist.Param()
    
    They are made available to you in render_* methods by calling self.parse_args(request)
    """

    def parse_args(self, request):
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