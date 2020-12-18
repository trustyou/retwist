import pytest_twisted
from twisted.web.resource import NoResource, Resource

import retwist
from tests.common import MyDummyRequest, _render


class HotelPage(Resource):

    def render_GET(self, request):
        hotel_id = request.path_args["hotel_id"]
        return hotel_id.encode()


class RestaurantPage(Resource):

    def render_GET(self, request):
        hotel_id = request.path_args[0]
        return hotel_id.encode()


@pytest_twisted.inlineCallbacks
def test_route_site():

    root = Resource()
    root.putChild(b"default", HotelPage())

    path_site = retwist.RouteSite(root)

    # Add a path with named parameters (get stored as dictionary)

    path_site.addRoute(r"/hotels/(?P<hotel_id>.*)/info", HotelPage())

    # Test that we get the correct request object

    request = MyDummyRequest([b"hotels", b"1234", b"info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)
    assert request.path_args == {
        "hotel_id": "1234"
    }

    # Test that request rendering receives tha arguments correctly

    yield _render(resource, request)
    response_str = b"".join(request.written)
    assert response_str == b"1234"

    # ... now let's add a path with unnamed parameters, which are passed as a tuple

    path_site.addRoute(r"/restaurants/(.*)/info", RestaurantPage())

    request = MyDummyRequest([b"restaurants", b"5678", b"info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, RestaurantPage)
    assert request.path_args == ("5678",)

    # Again, test that rendering works as expected

    yield _render(resource, request)
    response_str = b"".join(request.written)
    assert response_str == b"5678"

    # Test the fallback to regular Twisted path resolution

    request = MyDummyRequest([b"default"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)

    # Test 404

    request = MyDummyRequest([b"some", b"nonexistent", b"path"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, NoResource)
