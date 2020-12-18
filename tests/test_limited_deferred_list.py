import collections
import random

import pytest_twisted
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from retwist.util.limited_deferred_list import LimitedDeferredList


@pytest_twisted.inlineCallbacks
def test_limited_deferred_list():
    """
    Test that no more than max_concurrent Deferreds are run at the same time, and that results are returned in correct
    order.
    """

    max_concurrent = 2
    counter = collections.Counter()

    def make_deferred_factory(index):
        """
        Return a Deferred factory for testing purposes. Makes a Deferred which resolves with "Deferred {index} done"
        after a random time in [0, 10ms].
        :return: Function which, when invoked, returns a Deferred
        """
        def deferred_factory():
            counter["running"] += 1
            deferred = Deferred()

            def resolve_deferred():
                # Check that, at no point, there are more than max_concurrent Deferreds running
                assert counter["running"] <= max_concurrent
                deferred.callback("Deferred {} done".format(index))
                counter["running"] -= 1

            # Wait between 0 and 10ms before resolving. Do this to ensure Deferreds are run in shuffled order
            delay = random.random() * 0.01
            reactor.callLater(delay, resolve_deferred)

            return deferred
        return deferred_factory

    deferred_factories = [make_deferred_factory(index) for index in range(10)]
    defs = LimitedDeferredList(deferred_factories, max_concurrent)

    results = yield defs

    expected_results = ["Deferred {} done".format(index) for index in range(10)]
    assert expected_results == results


@pytest_twisted.inlineCallbacks
def test_synchronous_deferreds():
    """
    Test that deferreds that callback synchronously don't mess up our control flow.
    """

    def deferred_factory():
        deferred = Deferred()
        deferred.callback("done")
        return deferred

    # While we're at it, test that we accept an iterable for deferred_factories ...
    deferred_factories = (deferred_factory for _ in range(2))
    # ... and that max_concurrent can be larger than the number of Deferreds you schedule:
    defs = LimitedDeferredList(deferred_factories, 10)

    results = yield defs

    assert ["done", "done"] == results


@pytest_twisted.inlineCallbacks
def test_error_handling():

    counter = collections.Counter()

    def deferred_factory():
        deferred = Deferred()
        deferred.errback(RuntimeError("The Internet is broken"))
        return deferred

    deferred_factories = [deferred_factory]
    defs = LimitedDeferredList(deferred_factories, 2)

    def callback(result):
        # This should not run
        assert False

    def errback(failure):
        # This should run exactly once
        counter["errback"] += 1

    defs.addCallbacks(callback, errback)

    yield defs

    assert counter["errback"] == 1
