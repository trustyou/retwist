import pytest
from twisted.web.test.requesthelper import DummyRequest
from twisted.web.error import Error

import retwist


class DemoPage(retwist.ParamResource):

    id = retwist.Param(required=True)
    uuid = retwist.UUIDParam()
    show_details = retwist.BoolParam()
    def_param = retwist.BoolParam(name="def")


def test_param_resource():

    request = DummyRequest("/")
    request.addArg(b"id", b"1234")
    request.addArg(b"show_details", b"false")

    resource = DemoPage()
    args = resource.parse_args(request)
    assert args["id"] == "1234"
    assert args["show_details"] is False


def test_param_resource_override_name():

    request = DummyRequest("/")
    request.addArg(b"id", b"1234")
    request.addArg(b"def", b"true")

    resource = DemoPage()
    args = resource.parse_args(request)
    assert args["def"] is True


def test_param_resource_error():

    request = DummyRequest("/")
    request.addArg(b"id", b"1234")
    request.addArg(b"uuid", b"1234")

    resource = DemoPage()

    with pytest.raises(Error) as exc_info:
        resource.parse_args(request)

    assert exc_info.value.message == b"Error in parameter uuid: %s" % retwist.UUIDParam.MALFORMED_ERROR_MSG
