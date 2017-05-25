# retwist

Retwist allows convenient creation of RESTful JSON endpoints in Twisted. Features:

* Parsing of URL parameters from requests
* Handles encoding JSON responses, including support for good old JSONP

You implement JSON endpoints by subclassing `retwist.JsonResource`, and implementing the `json_GET` method.

## Example

Here's a simple demo page that parses a required ID parameter, and echoes it back in a JSON object:
    
    class DemoPage(retwist.JsonResource):
    
        isLeaf = True
    
        id = retwist.Param(required=True)
    
        def json_GET(self, request):
            # This method can also return a Deferred
            return self.parse_args(request)
            
See also examples folder.
