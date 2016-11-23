How to generate documentation
=============================


Requirements
------------

This tool uses Sphinx and read-the-doc theme. All required modules are listed in
src/requirements.txt. These requirements are addition to CSIT requirements
defined in requirements.txt.

The generated documentation needs Java script to be fully functional.

The generated documentation is in the directory _build.


How to generate documentation
-----------------------------

 - pull the last changes from git
 - run: ./run_doc.sh


What is documented
------------------

All modules which are in these directories are documented:
 - resources/libraries/python
 - resources/libraries/robot
 - tests

If you add / remove / rename a module or directory to one of these
directories, nothing is needed to be done.


How to add or change info in generated documentation
----------------------------------------------------

There are templates for
 - index
 - Python library documentation
 - Robot library documentation
 - Functional tests documentation
 - Performance tests documenation
in src/ directory.

You can add information you want at the beginning of the file, generated
documentation will be appended at the end of these files.

See index.rst for example. The information there was copy&pasted from fd.io
