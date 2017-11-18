import setuptools

version = "0.2"

setuptools.setup(
    name="retwist",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    description="Write JSON REST APIs in the Twisted framework",
    author="TrustYou",
    author_email="development@trustyou.com",
    version=version,
    download_url="https://github.com/trustyou/retwist/archive/v{}.tar.gz".format(version),
    url="https://github.com/trustyou/retwist",
    install_requires=[
        "twisted",
        "typing;python_version<'3.5'"
    ],
    extras_require={
        "sentry": ["raven"]
    }
)
