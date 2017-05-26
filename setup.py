import sys

import setuptools
from setuptools.command.test import test as TestCommand


INSTALL_REQUIRES = open("requirements.txt").readlines()

version = "0.1"


class PyTest(TestCommand):
    """
    Run pytest with Twisted plugin.
    """

    def run_tests(self):
        import pytest
        errno = pytest.main(["--twisted", "tests"])
        sys.exit(errno)


setuptools.setup(
    name="retwist",
    packages=setuptools.find_packages(),
    description="Write JSON REST APIs in the Twisted framework",
    author="TrustYou",
    author_email="development@trustyou.com",
    version=version,
    url="https://github.com/trustyou/retwist",
    install_requires=INSTALL_REQUIRES,

    test_suite="tests",
    tests_require=[
        "pytest",
        "pytest-twisted"
    ],
    cmdclass={'test': PyTest},

    platforms="any",
)
