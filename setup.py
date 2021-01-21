import io
import os.path

import setuptools

version = "0.4.2"

this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, "README.md")
with io.open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="retwist",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "retwist": ["py.typed"],
    },
    description="Write JSON REST APIs in the Twisted framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TrustYou",
    author_email="development@trustyou.com",
    version=version,
    download_url="https://github.com/trustyou/retwist/archive/v{}.tar.gz".format(version),
    url="https://github.com/trustyou/retwist",
    install_requires=[
        "twisted>16.4",
        "typing;python_version<'3.5'",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    extras_require={
        "sentry": ["sentry-sdk"],
        "jsonschema": [
            "jsonschema",
            # pyrsistent is a dependency of jsonschema, pinned to the latest Python 2-compatible version
            "pyrsistent<=0.16.1;python_version<'3'"
        ]
    }
)
