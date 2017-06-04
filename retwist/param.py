import re

import twisted.web.error


class Param(object):
    """
    Base class for retwist Parameters. Subclass and override parse() to implement custom parsing behavior. 
    """

    def __init__(self, required=False, default=None):
        """
        :param required: Throw 400 error if parameter is missing
        :param default: Default value, in case parameter missing 
        """
        if required and default:
            raise ValueError("Required parameters can't have a default")

        self.required = required
        self.default = default

    def parse_from_request(self, name, request):
        """
        Parse parameter by name from request object. Throws 400 client error if parameter is required, but missing.
        :param name: Name of parameter in query
        :param request: Twisted request object
        :return: Parsed value
        """
        name_bytes = name.encode()
        if name_bytes not in request.args:
            if self.default is not None:
                return self.default
            if self.required:
                raise twisted.web.error.Error(400, message=b"%s is required" % name_bytes)
            else:
                return None

        if len(request.args[name_bytes]) != 1:
            raise twisted.web.error.Error(400, message=b"Pass exactly one argument for %s" % name_bytes)

        val = request.args[name_bytes][0]
        return self.parse(val)

    def parse(self, val):
        """
        Parse parameter from raw string from URL query. Override this for custom parsing behavior.
        :param val: Value as received in URL
        :return: Parsed value
        """
        return val.decode()


class BoolParam(Param):
    """
    Evaluates to True if "true" is passed, False otherwise.
    """

    def parse(self, val):
        val = val.decode()
        if val is None or val == "false":
            return False
        if val == "true":
            return True
        raise twisted.web.error.Error(400, message=b"Boolean parameter must be 'true' or 'false'")


class IntParam(Param):
    """
    Parse an integer.
    """

    def __init__(self, min_val=None, max_val=None, *args, **kwargs):
        """
        :param min_val: Raise error if value is smaller than this
        :param max_val: Raise error if value is bigger than this
        """
        super(IntParam, self).__init__(*args, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def parse(self, val):
        val = val.decode()
        try:
            val = int(val)
        except (TypeError, ValueError):
            raise twisted.web.error.Error(400, b"Invalid integer: %s" % val.encode())
        if self.min_val is not None and val < self.min_val:
            raise twisted.web.error.Error(400, b"Minimum value %d" % self.min_val)
        if self.max_val is not None and val > self.max_val:
            raise twisted.web.error.Error(400, b"Minimum value %d" % self.max_val)
        return val


class EnumParam(Param):
    """
    Allow a pre-defined list of string values; raise 400 client error otherwise.
    """

    def __init__(self, enum, *args, **kwargs):
        """
        :param enum: List/tuple of allowed values, e.g. ("enabled", "disabled") 
        """
        super(EnumParam, self).__init__(*args, **kwargs)
        self.enum = frozenset(enum)

    def parse(self, val):
        val = val.decode()
        if val not in self.enum:
            error_msg = b"Parameter must be one of %s" % str(sorted(self.enum)).encode()
            raise twisted.web.error.Error(400, error_msg)
        return val


class LangParam(Param):
    """
    Parse language from "lang" URL parameter, or infer from Accept-Language HTTP header.
    """

    accept_language_re = re.compile("([a-z]{1,8}(?:-[a-z]{1,8})?)\s*(?:;\s*q\s*=\s*(1|0\.[0-9]+))?", re.IGNORECASE)

    def parse_from_request(self, name, request):
        if b"lang" in request.args:
            return super(LangParam, self).parse_from_request(name, request)
        return self.infer_lang(request)

    @classmethod
    def parse_accept_language(cls, accept_language_str):
        """
        Parse a list of accepted languages from an HTTP header.
        :param accept_language_str: HTTP Accept-Language value
        :return: A list of tuples (locale, weight), ordered by descending weight.
        """
        return sorted(
            (
                (match.group(1), match.group(2) or "1")
                for match in cls.accept_language_re.finditer(accept_language_str)
                if match.group(1) != "*" # ignore wildcard language
            ),
            key=lambda lang_weight: float(lang_weight[1]), reverse=True
        )

    def infer_lang(self, request):
        http_header = request.getHeader("Accept-Language")
        if http_header:
            try:
                locales = self.parse_accept_language(http_header)
            except (TypeError, ValueError):
                return self.default
            else:
                if locales:
                    return locales[0][0]
        return self.default


class VersionParam(Param):
    """
    Parse a version from a version string. Return a representation suitable for comparisons, e.g.:

    parse("5.9") < parse("5.10")
    """

    def parse(self, val):
        val = val.decode()
        try:
            return tuple(map(int, val.split(".")))
        except (TypeError, ValueError):
            raise twisted.web.error.Error(400, b"Invalid version literal")
