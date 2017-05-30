import pytest
import twisted.web.resource

import retwist
from tests.common import MyDummyRequest, _render


class HotelPage(twisted.web.resource.Resource):

    def render_GET(self, request):
        hotel_id = request.path_args["hotel_id"]
        return str(hotel_id)


class RestaurantPage(twisted.web.resource.Resource):

    def render_GET(self, request):
        hotel_id = request.path_args[0]
        return str(hotel_id)


@pytest.inlineCallbacks
def test_route_site():

    root = twisted.web.resource.Resource()
    root.putChild("default", HotelPage())

    path_site = retwist.RouteSite(root)

    # Add a path with named parameters (get stored as dictionary)

    path_site.addRoute(r"/hotels/(?P<hotel_id>.*)/info", HotelPage())

    # Test that we get the correct request object

    request = MyDummyRequest(["hotels", "1234", "info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)
    assert request.path_args == {
        "hotel_id": "1234"
    }

    # Test that request rendering receives tha arguments correctly

    yield _render(resource, request)
    response_str = "".join(request.written)
    assert response_str == "1234"

    # ... now let's add a path with unnamed parameters, which are passed as a tuple

    path_site.addRoute(r"/restaurants/(.*)/info", RestaurantPage())

    request = MyDummyRequest(["restaurants", "5678", "info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, RestaurantPage)
    assert request.path_args == ("5678",)

    # Again, test that rendering works as expected

    yield _render(resource, request)
    response_str = "".join(request.written)
    assert response_str == "5678"

    # Test the fallback to regular Twisted path resolution

    request = MyDummyRequest(["default"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)

    # Test 404

    request = MyDummyRequest(["some", "nonexistent", "path"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, twisted.web.resource.NoResource)