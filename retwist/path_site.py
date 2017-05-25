import re

import twisted.web.resource
import twisted.web.server


class PathSite(twisted.web.server.Site):
    """
    Twisted site which allows looking up resources by paths. Paths are regular expressions which match the entire
    request path, e.g. "/hotels/1234/info".
    
    Paths can have placeholders in them, which are passed as arguments to resources.
    """

    def __init__(self, resource=None, *args, **kwargs):
        """
        :param resource: Root resource for Twisted's standard Site implementation. Pass a resource if you want to fall
        back to Twisted's default resource lookup mechanism in case no patch matches. If None is passed, defaults to a
        NoResource() instance. 
        """
        resource = resource or twisted.web.resource.NoResource()
        twisted.web.server.Site.__init__(self, resource, *args, **kwargs)
        self.paths = {}

    def addPath(self, path, resource_class):
        """
        Register a handler resource for a path.
        :param path: Regular expression string. For matching requests, resource_class will be instantiated and returned
        If there are named groups in the regular expression, these are passed as keyword arguments to the resource class
        constructor. Otherwise, if there are unnamed groups, they are passed as positional arguments. Don't mix the two
        types.
        :param resource_class: A resource class (not instance!) which will be instantiated with arguments parsed from
        groups in path for every matching request.
        """
        path_re = re.compile(path)
        self.paths[path_re] = resource_class

    def getResourceFor(self, request):
        """
        Check if a path matches this request. Fall back to Twisted default lookup behavior otherwise.
        :param request: Twisted request instance
        :return: Resource to handle this request
        """
        for path_re, resource_class in self.paths.items():
            match = path_re.match(request.path)
            if match:
                kwargs = match.groupdict()
                args = match.groups() if not kwargs else []
                return resource_class(*args, **kwargs)

        return twisted.web.server.Site.getResourceFor(self, request)