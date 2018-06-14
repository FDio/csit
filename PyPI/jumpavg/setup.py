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
    name="jumpavg",
    version="0.1.2",  # This is currently the only place listing the version.
    description="Library for finding changes in time series by grouping results.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # TODO: Create a separate webpage for jumpavg library.
    url="https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg;hb=refs/heads/master",
    author="Cisco Systems Inc. and/or its affiliates",
    author_email="csit-dev@lists.fd.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        # Pick your license as you wish
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        # TODO: Test which Python versions is the code compatible with.
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    keywords="progression regression anomaly detection",
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
        "Source": "https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/jumpavg;hb=refs/heads/master",
    },
)
