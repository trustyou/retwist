from twisted.web.error import Error
from twisted.web.http import NOT_ALLOWED
from twisted.web.static import File


class NoListingFile(File):
    """
    Serve files, but disallow directory listing.
    """

    def directoryListing(self):
        # type: () -> None
        raise Error(NOT_ALLOWED, b"Not allowed")
