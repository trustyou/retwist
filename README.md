# retwist

Retwist allows convenient creation of RESTful JSON endpoints in Twisted. Features:

* Routes: Mapping path patterns like `r"/hotels/(.*)/info"` to Twisted Resources. Instead of using the Twisted
`getChild()` lookup mechanism.
* Parsing of URL parameters from requests. Parameters are defined in `Resource` class scope, e.g.
`type = retwist.EnumParam(["html", "json])`.
* Handles encoding JSON responses, including support for good old JSONP.

You implement JSON endpoints by subclassing `retwist.JsonResource`, and implementing the `json_GET` method.

## Example

Here's a simple demo page that parses a required ID parameter, and echoes it back in a JSON object. Note how we register
a route "/echo". 
    
    class DemoPage(retwist.JsonResource):
    
        isLeaf = True
    
        id = retwist.Param(required=True)
    
        def json_GET(self, request):
            # This method can also return a Deferred
            args = request.url_args
            return {
                "msg": "You passed ID {}".format(args["id"])
            }
            
    site = retwist.RouteSite()
    site.addRoute(r"/echo", EchoPage())
    twisted.internet.reactor.listenTCP(8080, site)
    twisted.internet.reactor.run()
            
See also [examples folder](retwist/examples).

## Sentry error reporting

Install retwist with the `[sentry]` extra, and enable Sentry reporting like so:

    from raven import Client
    client = Client(your_sentry_dsn)

    from retwist.util.sentry import enable_sentry_reporting
    enable_sentry_reporting(client)

This will capture any errors logged to [Twisted's logging system](http://twistedmatrix.com/documents/current/core/howto/logging.html)
 and forward exceptions to Sentry.