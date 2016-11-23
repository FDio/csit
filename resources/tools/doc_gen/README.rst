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


How to document code for perfect results
----------------------------------------

Follow PEP8 and guidelines on wiki https://wiki.fd.io/view/CSIT/Documentation

This is the best practice when we use Sphinx:

Python code
+++++++++++

.. code:: python

    """Module description, start with one-short-sentence-description.

    Add more descriptive text.

    You can add a list (there must be an empty line):

    - item,
    - second item.

    or numbered list (there also must be an empty line):

    #. The first item,
    #. The second item.

    """

    class ExampleClass(BaseClass):
        """Start with one-short-sentence-description.

        Add more descriptive text.
        """

        def example_function(parameter, param_def="def"):
            """Start with one-short-sentence-description.

            Add more descriptive text, and / or example.

            :Example:

            followed by a blank line!

            You can use also:
            .. seealso:: blabla
            .. warnings:: blabla
            .. note:: blabla
            .. todo:: blabla

            :param parameter: The first parameter. Capital letter at the
            beginning, full stop at the end, 80 characters long lines.
            :param param_def: The parameter with default value.
            :type param: str, int, dict, ... Use python data types.
            :type param_def: str
            :raises: ValueError - describe when this exception is raised.
            :returns: Nice string.
            :rtype: str
            """


Robot code
++++++++++

TBD
