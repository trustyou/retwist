import json
import re
from typing import Any, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar, Union
from uuid import UUID

from twisted.web.error import Error
from twisted.web.http import Request, BAD_REQUEST

try:
    from jsonschema import ValidationError
    from jsonschema.validators import validator_for
except ImportError:
    def validator_for(*args, **kwargs):  # type: ignore
        raise NotImplementedError("Install with jsonschema extra to enable validating JSON parameters")

    class ValidationError(Exception):  # type: ignore
        pass


T = TypeVar("T")


class BaseParam(Generic[T]):
    """
    Base class for retwist Parameters. Subclass and override parse() to implement custom parsing behavior.
    """

    encoding = "utf-8"

    def __init__(self, required=False, default=None, name=None):
        # type: (bool, Optional[T], Optional[str]) -> None
        """
        :param required: Throw 400 error if parameter is missing
        :param default: Default value, in case parameter missing
        :param name: Parameter name in the URL. Use this parameter if your parameter name is a reserved Python keyword
        """
        if required and default:
            raise ValueError("Required parameters can't have a default")

        self.required = required
        self.default = default
        self.name = name

    def parse_from_request(self, name, request):
        # type: (str, Request) -> Optional[T]
        """
        Parse parameter by name from request object. Throws 400 client error if parameter is required, but missing.
        :param name: Name of parameter in query
        :param request: Twisted request object
        :return: Parsed value
        """
        name_bytes = name.encode(self.encoding)
        if name_bytes not in request.args:
            if self.default is not None:
                return self.default
            if self.required:
                raise Error(BAD_REQUEST, message=b"Required")
            else:
                return None

        if len(request.args[name_bytes]) != 1:
            raise Error(BAD_REQUEST, message=b"Pass exactly one argument")

        val = request.args[name_bytes][0]
        return self.parse(val)

    def parse(self, val):
        # type: (bytes) -> T
        """
        Parse parameter from raw string from URL query. Override this for custom parsing behavior.
        :param val: Value as received in URL
        :return: Parsed value
        """
        raise NotImplementedError


class Param(BaseParam[str]):

    def parse(self, val):
        # type: (bytes) -> str
        """
        Parse parameter from raw string from URL query. Override this for custom parsing behavior.
        :param val: Value as received in URL
        :return: Parsed value
        """
        return val.decode(self.encoding)


class BoolParam(BaseParam[bool]):
    """
    Evaluates to True if "true" is passed, False otherwise.
    """

    def parse(self, val):
        # type: (bytes) -> bool
        if val is None or val == b"false":
            return False
        if val == b"true":
            return True
        raise Error(BAD_REQUEST, message=b"Boolean parameter must be 'true' or 'false'")


class IntParam(BaseParam[int]):
    """
    Parse an integer.
    """

    def __init__(self, min_val=None, max_val=None, *args, **kwargs):
        # type: (Optional[int], Optional[int], *Any, **Any) -> None
        """
        :param min_val: Raise error if value is smaller than this
        :param max_val: Raise error if value is bigger than this
        """
        super(IntParam, self).__init__(*args, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def parse(self, val):
        # type: (bytes) -> int
        try:
            val_int = int(val)
        except (TypeError, ValueError):
            raise Error(BAD_REQUEST, b"Invalid integer: %s" % val)
        if self.min_val is not None and val_int < self.min_val:
            raise Error(BAD_REQUEST, b"Minimum value %d" % self.min_val)
        if self.max_val is not None and val_int > self.max_val:
            raise Error(BAD_REQUEST, b"Maximum value %d" % self.max_val)
        return val_int


class EnumParam(BaseParam[str]):
    """
    Allow a pre-defined list of string values; raise 400 client error otherwise.
    """

    def __init__(self, enum, *args, **kwargs):
        # type: (Iterable[str], *Any, **Any) -> None
        """
        :param enum: List/tuple of allowed values, e.g. ("enabled", "disabled")
        """
        super(EnumParam, self).__init__(*args, **kwargs)
        self.enum = frozenset(enum)

    def parse(self, val):
        # type: (bytes) -> str
        val_str = val.decode(self.encoding)
        if val_str not in self.enum:
            error_msg = b"Parameter must be one of %s" % str(sorted(self.enum)).encode()
            raise Error(BAD_REQUEST, error_msg)
        return val_str


class LangParam(Param):
    """
    Parse language from "lang" URL parameter, or infer from Accept-Language HTTP header.
    """

    accept_language_re = re.compile(r"([a-z]{1,8}(?:-[a-z]{1,8})?)\s*(?:;\s*q\s*=\s*(1|0\.[0-9]+))?", re.IGNORECASE)

    def parse_from_request(self, name, request):
        # type: (str, Request) -> Optional[str]
        if b"lang" in request.args:
            return super(LangParam, self).parse_from_request(name, request)
        return self.infer_lang(request)

    @classmethod
    def parse_accept_language(cls, accept_language_str):
        # type: (str) -> List[Tuple[str, str]]
        """
        Parse a list of accepted languages from an HTTP header.
        :param accept_language_str: HTTP Accept-Language value
        :return: A list of tuples (locale, weight), ordered by descending weight.
        """
        return sorted(
            (
                (match.group(1), match.group(2) or "1")
                for match in cls.accept_language_re.finditer(accept_language_str)
                if match.group(1) != "*"  # ignore wildcard language
            ),
            key=lambda lang_weight: float(lang_weight[1]), reverse=True
        )

    def infer_lang(self, request):
        # type: (Request) -> str
        http_header = request.getHeader("Accept-Language")
        default_lang = str(self.default)  # type: str
        if http_header:
            try:
                locales = self.parse_accept_language(http_header)
            except (TypeError, ValueError):
                return default_lang
            else:
                if locales:
                    return locales[0][0]
        return default_lang


class VersionParam(BaseParam[Tuple[int, ...]]):
    """
    Parse a version from a version string. Return a representation suitable for comparisons, e.g.:

    parse("5.9") < parse("5.10")
    """

    def parse(self, val):
        # type: (bytes) -> Tuple[int, ...]
        try:
            return tuple(map(int, val.split(b".")))
        except (TypeError, ValueError):
            raise Error(BAD_REQUEST, b"Invalid version literal")


# Approximate representation of JSON data, for type annotations
_JSON_OBJECT_TYPE = Dict[str, Any]
_JSON_TYPE = Union[None, bool, int, float, str, list, _JSON_OBJECT_TYPE]


class JsonParam(BaseParam[_JSON_TYPE]):
    """
    Parse a parameter encoded as JSON. You can optionally verify its data format by passing a https://json-schema.org/
    """

    # Some common JSON schema types. Can be passed to `JsonParam.array(items=JsonParam.NUMBER_TYPE)`, for example.
    NUMBER_TYPE = {"type": "number"}
    STRING_TYPE = {"type": "string"}
    UUID_TYPE = {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}

    def __init__(self, schema=None, *args, **kwargs):
        # type: (Any, *Any, **Any) -> None
        """
        :param schema: JSON schema (draft 7 compatible), or None if format shouldn't be checked
        """
        super(JsonParam, self).__init__(*args, **kwargs)
        if schema is None:
            self.validator = None
        else:
            validator_class = validator_for(schema)
            validator_class.check_schema(schema)
            self.validator = validator_class(schema)

    def parse(self, val):
        # type: (bytes) -> _JSON_TYPE
        try:
            data = json.loads(val)  # type: _JSON_TYPE
            if self.validator is not None:
                self.validator.validate(data)
        except ValueError as ex:
            error_message = str(ex).encode("utf-8")
            raise Error(BAD_REQUEST, b"Invalid JSON: %s" % error_message)
        except ValidationError as ex:
            error_message = ex.message.encode("utf-8")
            raise Error(BAD_REQUEST, b"JSON schema error: %s" % error_message)
        else:
            return data

    @classmethod
    def array(cls, items=None, min_items=None, max_items=None, *args, **kwargs):
        # type: (Optional[Dict[str, Any]], Optional[int], Optional[int], *Any, **Any) -> JsonParam
        """
        Parse a parameter encoded as a JSON array.

        :param items: Schema to apply for array items (optional)
        :param min_items: Minimum number of items (optional)
        :param max_items: Maximum number of items (optional)
        """
        schema = {"type": "array"}  # type: _JSON_OBJECT_TYPE
        if items is not None:
            schema["items"] = items
        if min_items is not None:
            schema["minItems"] = min_items
        if max_items is not None:
            schema["maxItems"] = max_items
        return cls(schema, *args, **kwargs)


class UUIDParam(BaseParam[UUID]):
    """
    Parameter that verifies it's a valid UUID.
    """

    MALFORMED_ERROR_MSG = b"Malformed UUID"

    def parse(self, val):
        # type: (bytes) -> UUID
        val_str = val.decode()
        try:
            return UUID(val_str)
        except ValueError:
            raise Error(BAD_REQUEST, message=UUIDParam.MALFORMED_ERROR_MSG)
