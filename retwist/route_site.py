import re
from typing import Any, Dict, Pattern

import twisted.web.resource
import twisted.web.server


class RouteSite(twisted.web.server.Site):
    """
    Twisted site which allows looking up resources by routes. Routes are regular expressions which match the entire
    request path, e.g. "/hotels/1234/info".
    
    Routes can have placeholders in them, which are stored as arguments in request.path_args before your render_* sees
    it.
    """

    def __init__(self, resource=None, *args, **kwargs):
        # type: (twisted.web.resource.Resource, *Any, **Any) -> None
        """
        :param resource: Root resource for Twisted's standard Site implementation. Pass a resource if you want to fall
        back to Twisted's default resource lookup mechanism in case no route matches. If None is passed, defaults to a
        NoResource() instance. 
        """
        resource = resource or twisted.web.resource.NoResource()
        twisted.web.server.Site.__init__(self, resource, *args, **kwargs)
        self.routes = {}  # type: Dict[Pattern, twisted.web.resource.Resource]

    def addRoute(self, route, resource):
        # type: (str, twisted.web.resource.Resource) -> None
        """
        Register a handler resource for a path.
        :param route: Regular expression string. If a request's path matches this regex, this resource's render_*
        method will be called with it. The request will have arguments parsed from the route added as request.path_args.
        If there are named groups in the regular expression, the path arguments are passed as a dictionary. If they're
        unnamed, they're passed as a tuple.
        :param resource: A resource instance. Its render_* method will be called for requests matching route pattern.
        """
        route_re = re.compile(route)
        self.routes[route_re] = resource

    def getResourceFor(self, request):
        # type: (twisted.web.http.Request) -> twisted.web.resource.Resource
        """
        Check if a route matches this request. Fall back to Twisted default lookup behavior otherwise.
        :param request: Twisted request instance
        :return: Resource to handle this request
        """
        request.site = self
        for route_re, resource in self.routes.items():
            path = request.path.decode()
            match = route_re.match(path)
            if match:
                request.path_args = match.groupdict() or match.groups()
                return resource

        return twisted.web.server.Site.getResourceFor(self, request)