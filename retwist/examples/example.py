import twisted.internet.reactor
import twisted.web.server

import retwist


class DemoPage(retwist.JsonResource):

    isLeaf = True

    id = retwist.Param(required=True)

    def json_GET(self, request):
        return self.parse_args(request)


if __name__ == "__main__":

    site = twisted.web.server.Site(DemoPage())
    port = 8080
    twisted.internet.reactor.listenTCP(port, site)

    print("Demo starting ... now try these requests:")
    print("http://localhost:{}/?id=1234 (Should echo parameter)".format(port))
    print("http://localhost:{} (Returns error, since 'id' is required)".format(port))
    print("Interrupt with Ctrl+C to quit")

    twisted.internet.reactor.run()
