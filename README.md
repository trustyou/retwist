# retwist

Retwist allows convenient creation of RESTful JSON endpoints in Twisted. Features:

* Routes: Mapping path patterns like `r"/hotels/(.*)/info"` to Twisted Resources. Instead of using the Twister
`getChild()` lookup mechanism.
* Parsing of URL parameters from requests. Parameters are defined in `Resource` class scope, e.g.
`type = retwist.EnumParam(["html", "json])`.
* Handles encoding JSON responses, including support for good old JSONP.

You implement JSON endpoints by subclassing `retwist.JsonResource`, and implementing the `json_GET` method.

## Example

Here's a simple demo page that parses a required ID parameter, and echoes it back in a JSON object. Note how we register
a path "/echo". 
    
    class DemoPage(retwist.JsonResource):
    
        isLeaf = True
    
        id = retwist.Param(required=True)
    
        def json_GET(self, request):
            # This method can also return a Deferred
            id = self.parse_args(request)["id"]
            return {
                "msg": "You passed ID {}".format(id)
            }
            
    site = retwist.PathSite()
    site.addPath(r"/echo", EchoPage)
    twisted.internet.reactor.listenTCP(8080, site)
    twisted.internet.reactor.run()
            
See also [examples folder](retwist/examples).
