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

```python
import retwist, twisted.internet.reactor

class DemoPage(retwist.JsonResource):

    isLeaf = True

    id = retwist.Param(required=True)

    # Use the "name" argument for parameters whose names are reserved Python keywords:
    from_param = retwist.Param(name="from")

    def json_GET(self, request):
        # This method can also return a Deferred
        args = request.url_args
        return {
            "msg": "You passed ID {} and from {}".format(args["id"], args.get("from"))
        }

site = retwist.RouteSite()
site.addRoute(r"/echo", DemoPage())
twisted.internet.reactor.listenTCP(8080, site)
twisted.internet.reactor.run()
```

See also [examples folder](retwist/examples).

## JSON parameters

Retwist can parse JSON-encoded parameters, and with the `[jsonschema]` extra installed, perform schema validations on
the data.

For example, this resource will parse the data passed for the "config" parameter, and return a 400 client error if it
was invalid JSON, or did not comply with the specified schema:

```python
import retwist

class JsonDemoPage(retwist.JsonResource):
 
    config = retwist.JsonParam(schema={"type": "object"})

    def json_GET(self, request):
        # You can assume request.url_args["config"] to be a dictionary here
        # ...
```

## Sentry error reporting

Install retwist with the `[sentry]` extra, and enable Sentry reporting like so:

```python
import sentry_sdk
sentry_sdk.init(dsn="...", release="...")

from retwist.util.sentry import enable_sentry_reporting
enable_sentry_reporting()

# This is useful to redirect Twisted log messages to Python's logging module:
from retwist.util.logs import redirect_twisted_logging
redirect_twisted_logging()
```

This will capture any errors logged to [Twisted's logging system](http://twistedmatrix.com/documents/current/core/howto/logging.html)
 and forward exceptions to Sentry. Starting from retwist 0.3, this reports the request URL, headers and data to Sentry.

## Development Notes

Retwist comes with a [tox configuration](tox.ini) to run its test suite on all supported Python versions, as well as a
linting and type checking step.

It's possible to install all required Python versions locally via [pyenv](https://github.com/pyenv/pyenv).
Alternatively, use the [kiwicom/tox Docker image](https://hub.docker.com/r/kiwicom/tox) to run the test suite:

```shell
docker pull kiwicom/tox

docker container run \
    --mount src=$PWD,target=/retwist,type=bind \
    --interactive --tty --rm \
    --dns 8.8.8.8 \  # Prevents a DNS issue which occurs on some Linux hosts. This is a Google DNS server, but any other would work too
    kiwicom/tox \
    /bin/bash -c "cd /retwist && find -name '*.pyc' -delete && tox"  # Delete stale *.pyc files to avoid errors on Python 2
```