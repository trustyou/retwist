import collections
from typing import Any, Callable, Iterable

from twisted.internet.defer import Deferred, FirstError
from twisted.python.failure import Failure


class LimitedDeferredList(Deferred):
    """
    Run a list of Deferreds in parallel, much like DeferredList, but limit the number of concurrently executed
    Deferreds.

    Useful if you need to run 100 things in parallel, but don't want to run more than 10 at once, e.g. to limit access
    to system resources.

    Unlike DeferredList, you can't pass a list of Deferreds to this class, since they would be running already. Instead,
    pass a list of factory methods that make the Deferred on demand.

    If any single one of the Deferreds fails, the overall LimitedDeferredList will errback with a FirstError failure,
    just like the DeferredList.
    """

    def __init__(self, deferred_factories, max_concurrent):
        # type: (Iterable[Callable[[], Deferred]], int) -> None
        """
        :param deferred_factories: A list of callables which, when invoked without arguments, return a Deferred.
        :param max_concurrent: Run no more than max_concurrent Deferreds at the same time.
        """
        Deferred.__init__(self)

        # Index the Deferreds so we can order the results when they callback
        indexed_factories = enumerate(deferred_factories)
        self.deferred_factories = collections.deque(indexed_factories)

        self.results = [None] * len(self.deferred_factories)
        self.counter = 0

        # Start up max_concurrent Deferreds! Later, we start a new Deferred for every one that callbacks. So we don't
        # even need to store max_concurrent
        for _ in range(max_concurrent):
            self.__schedule_deferred()

    def __deferred_callback(self, result, index):
        # type: (Any, int) -> None
        """
        Callback for every one of the scheduled Deferreds.
        :param result: Result of the Deferred.
        :param index: Index in overall result list.
        """
        self.counter -= 1
        self.results[index] = result
        # If there are no other Deferreds running and no more to be scheduled, we're all done. Resolve with the results
        # list
        if not self.__schedule_deferred() and self.counter == 0:
            self.callback(self.results)

    def __deferred_errback(self, failure, index):
        # type: (Failure, int) -> None
        """
        Errback for every one of the scheduled Deferreds. Make the whole LimitedDeferredList fail.
        :param failure: Failure object.
        :param index: Index in overall result list.
        """
        if not self.called:
            self.errback(FirstError(failure, index))

    def __schedule_deferred(self):
        # type: () -> bool
        """
        Schedule the next available Deferred.
        :return: True if a Deferred was scheduled, False if not (i.e. we're done with our work)
        """
        if self.deferred_factories:
            self.counter += 1
            index, deferred_factory = self.deferred_factories.pop()
            deferred = deferred_factory()  # type: Deferred
            deferred.addCallback(self.__deferred_callback, index)
            deferred.addErrback(self.__deferred_errback, index)
            return True
        return False
