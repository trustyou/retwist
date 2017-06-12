from twisted.internet import reactor

import retwist


class EchoPage(retwist.JsonResource):

    isLeaf = True

    id = retwist.Param(required=True)

    def json_GET(self, request):
        return request.url_args


if __name__ == "__main__":

    site = retwist.RouteSite()
    site.addRoute(r"/echo", EchoPage())

    port = 8080
    reactor.listenTCP(port, site)

    print("Demo starting ... now try these requests:")
    print("http://localhost:{}/echo?id=1234 (Should echo parameter)".format(port))
    print("http://localhost:{}/echo (Returns error, since 'id' is required)".format(port))
    print("Interrupt with Ctrl+C to quit")

    reactor.run()
