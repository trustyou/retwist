import setuptools
from setuptools.command.test import test as TestCommand

import sys

INSTALL_REQUIRES = open("requirements.txt").readlines()

version = "0.1"


class PyTest(TestCommand):

    def run_tests(self):
        import pytest
        errno = pytest.main(["--twisted"])
        sys.exit(errno)


setuptools.setup(
    name="retwist",
    packages=["retwist"],
    description="Write JSON REST APIs in the Twisted framework",
    author="TrustYou",
    author_email="development@trustyou.com",
    version=version,
    install_requires=INSTALL_REQUIRES,

    test_suite="tests",
    tests_require=[
        "pytest ~= 3.0",
        "pytest-twisted ~= 1.5"
    ],
    cmdclass = {'test': PyTest},

    platforms="any",
)