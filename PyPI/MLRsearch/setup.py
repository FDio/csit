"""A setup module for setuptools.

See:
https://packaging.python.org/en/latest/distributing.html

TODO: Move as much as possible into setup.cfg
"""

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, u"README.rst"), encoding=u"utf-8") as f:
    long_description = f.read()

setup(
    name=u"MLRsearch",
    version=u"0.4.0",  # This is currently the only place listing the version.
    description=u"Library for speeding up binary search using shorter measurements.",
    long_description=long_description,
    long_description_content_type=u"text/x-rst",
    # TODO: Create a separate webpage for MLRsearch library.
    url=u"https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch;hb=refs/heads/master",
    author=u"Cisco Systems Inc. and/or its affiliates",
    author_email=u"csit-dev@lists.fd.io",
    classifiers=[
        u"Development Status :: 3 - Alpha",
        u"Intended Audience :: Science/Research",
        u"Intended Audience :: Telecommunications Industry",
        u"License :: OSI Approved :: Apache Software License",
        u"Programming Language :: Python :: 3.6",
        u"Topic :: System :: Networking"
    ],
    keywords=u"binary search throughput networking",
    packages=find_packages(exclude=[]),
    python_requires=u"~=3.6",
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
        u"Source": u"https://gerrit.fd.io/r/gitweb?p=csit.git;a=tree;f=PyPI/MLRsearch;hb=refs/heads/master",
    },
)
