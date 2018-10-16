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
        "twisted==18.9.0",
        "typing;python_version<'3.5'"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    extras_require={
        "sentry": ["raven"]
    }
)
