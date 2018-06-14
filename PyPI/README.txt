Directories here hold code to be released into Python Package Index (PyPI).

Mosly libraries, so people could expect them in resources/libraries/python/.
But these libraries cannot be there, because that is a package hierarchy
used by robot code, but we want the libraries here
to be NOT read from cloned CSIT git repo, but from pip.
