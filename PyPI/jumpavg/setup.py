#!/usr/bin/env python3

"""A setup module for setuptools.

See:
https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import (setup, find_packages)
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, u"README.rst"), encoding=u"utf-8") as f:
    long_description = f.read()

setup(
    name=u"jumpavg",
    version=u"0.2.0",  # This is currently the only place listing the version.
    description=(
        u"Library for locating changes in time series by grouping results."
    ),
    long_description=long_description,
    long_description_content_type=u"text/x-rst",
    # TODO: Create a separate webpage for jumpavg library.
    url=(
        u"https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg"
        u";hb=refs/heads/master"
    ),
    author=u"Cisco Systems Inc. and/or its affiliates",
    author_email=u"csit-dev@lists.fd.io",
    classifiers=[
        u"Development Status :: 3 - Alpha",
        u"Intended Audience :: Science/Research",
        # Pick your license as you wish
        u"License :: OSI Approved :: Apache Software License",
        u"Natural Language :: English",
        # TODO: Test which Python versions is the code compatible with.
        u"Programming Language :: Python :: 2.7",
        u"Topic :: Scientific/Engineering :: Information Analysis"
    ],
    keywords=u"progression regression anomaly detection statistics bits",
    packages=find_packages(exclude=[]),
    python_requires="~=3.6",
    install_requires=[],
    # TODO: Include simulator and tests.
    extras_require={
    },
    package_data={
    },
    entry_points={
        u"console_scripts": [
        ],
    },
    project_urls={
        u"Bug Reports": u"https://jira.fd.io/projects/CSIT/issues",
        u"Source": (
            u"https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg"
            u";hb=refs/heads/master"
        ),
    },
)
