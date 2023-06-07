#!/usr/bin/env python3

"""A setup module for setuptools.

See:
https://packaging.python.org/en/latest/distributing.html
"""

from os import path
from io import open

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="jumpavg",
    version="0.4.0",  # This is currently the only place listing the version.
    description=(
        "Library for locating changes in time series by grouping results."
    ),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # TODO: Create a separate webpage for jumpavg library.
    url=(
        "https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg"
        ";hb=refs/heads/master"
    ),
    author="Cisco Systems Inc. and/or its affiliates",
    author_email="csit-dev@lists.fd.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        # Pick your license as you wish
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        # TODO: Test which Python versions is the code compatible with.
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="progression regression anomaly detection statistics bits",
    packages=find_packages(exclude=[]),
    python_requires="~=3.8",
    install_requires=[],
    # TODO: Include simulator and tests.
    extras_require={},
    package_data={},
    entry_points={
        "console_scripts": [],
    },
    project_urls={
        "Bug Reports": "https://jira.fd.io/projects/CSIT/issues",
        "Source": (
            "https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg"
            ";hb=refs/heads/master"
        ),
    },
)
