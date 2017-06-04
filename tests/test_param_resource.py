from twisted.web.test.requesthelper import DummyRequest

import retwist


class DemoPage(retwist.ParamResource):

    id = retwist.Param(required=True)
    show_details = retwist.BoolParam()


def test_param_resource():

    request = DummyRequest("/")
    request.addArg(b"id", b"1234")
    request.addArg(b"show_details", b"false")

    resource = DemoPage()
    args = resource.parse_args(request)
    assert args["id"] == "1234"
    assert args["show_details"] is False