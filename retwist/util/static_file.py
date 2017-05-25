import twisted.web.error
import twisted.web.static


class NoListingFile(twisted.web.static.File):
    """
    Serve files, but disallow directory listing.
    """

    def directoryListing(self):
        raise twisted.web.error.Error(405, "Not allowed")