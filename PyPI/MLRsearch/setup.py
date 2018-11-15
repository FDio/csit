"""A setup module for setuptools.

See:
https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="MLRsearch",
    version="0.2.0",  # This is currently the only place listing the version.
    description="Library for speeding up binary search using shorter measurements.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # TODO: Create a separate webpage for MLRsearch library.
    url="https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch;hb=refs/heads/master",
    author="Cisco Systems Inc. and/or its affiliates",
    author_email="csit-dev@lists.fd.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        # Pick your license as you wish
        "License :: OSI Approved :: Apache Software License",
        # TODO: Test which Python versions is the code compatible with.
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Networking"
    ],
    keywords="binary search throughput networking",
    packages=find_packages(exclude=[]),
    # TODO: python_requires="~=2.7"
    install_requires=[],
    # TODO: Include simulator and tests.
    extras_require={
    },
    package_data={
    },
    entry_points={
        "console_scripts": [
        ],
    },
    project_urls={
        "Bug Reports": "https://jira.fd.io/projects/CSIT/issues",
        "Source": "https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch;hb=refs/heads/master",
    },
)
