import setuptools

version = "0.1"

setuptools.setup(
    name="retwist",
    packages=setuptools.find_packages(),
    description="Write JSON REST APIs in the Twisted framework",
    author="TrustYou",
    author_email="development@trustyou.com",
    version=version,
    url="https://github.com/trustyou/retwist",
    install_requires=[
        "twisted",
        "typing;python_version<'3.5'"
    ]
)
