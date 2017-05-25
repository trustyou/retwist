import twisted.web.resource

import retwist
from tests.common import MyDummyRequest


class HotelPage(twisted.web.resource.Resource):

    def __init__(self, hotel_id=None, *args, **kwargs):
        twisted.web.resource.Resource.__init__(self, *args, **kwargs)
        self.hotel_id = hotel_id


class RestaurantPage(twisted.web.resource.Resource):

    def __init__(self, restaurant_id, *args, **kwargs):
        twisted.web.resource.Resource.__init__(self, *args, **kwargs)
        self.restaurant_id = restaurant_id



def test_path_site():

    root = twisted.web.resource.Resource()
    root.putChild("default", HotelPage("default"))

    path_site = retwist.PathSite(root)
    # Add a path with named parameters (get turned into keyword arguments)
    path_site.addPath(r"/hotels/(?P<hotel_id>.*)/info", HotelPage)
    # ... and one without (get turned into positional arguments)
    path_site.addPath(r"/restaurants/(.*)/info", RestaurantPage)

    # Smoke test

    request = MyDummyRequest(["hotels", "1234", "info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)
    assert resource.hotel_id == "1234"

    request = MyDummyRequest(["restaurants", "5678", "info"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, RestaurantPage)
    assert resource.restaurant_id == "5678"

    # Test the fallback to regular Twisted path resolution

    request = MyDummyRequest(["default"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, HotelPage)
    assert resource.hotel_id == "default"

    # Test 404

    request = MyDummyRequest(["some", "nonexistent", "path"])
    resource = path_site.getResourceFor(request)
    assert isinstance(resource, twisted.web.resource.NoResource)