#!/usr/bin/python

# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from os import walk, listdir
from os.path import isfile, isdir, join, getsize

# Temporary working directory. It is created and deleted by run_doc.sh
WORKING_DIR = "tmp"

# Directory with resources to be documented.
RESOURCES_DIR = "resources"

# Directory with libraries (python, robot) to be documented.
LIB_DIR = "libraries"

# Directory with tests (func, perf) to be documented.
TESTS_DIR = "tests"

PY_EXT = ".py"
RF_EXT = ".robot"

PATH_PY_LIBS = join(WORKING_DIR, RESOURCES_DIR, LIB_DIR, "python")
PATH_RF_LIBS = join(WORKING_DIR, RESOURCES_DIR, LIB_DIR, "robot")
PATH_TESTS = join(WORKING_DIR, TESTS_DIR)

# Sections in rst files
rst_toc = """
.. toctree::
"""

rst_py_module = """
.. automodule:: {}.{}
    :members:
    :undoc-members:
    :show-inheritance:
"""

rst_rf_keywords = """
.. robot-keywords::
   :source: {}
"""

rst_rf_tests = """
.. robot-tests::
   :source: {}
"""


def get_files(path, extension):
    """Generates the list of files to process.

    :param path: Path to files.
    :param extension: Extension of files to process. If it is the empty string,
    all files will be processed.
    :type path: str
    :type extension: str
    :returns: List of files to process.
    :rtype: list
    """

    file_list = list()
    for root, dirs, files in walk(path):
        for filename in files:
            if extension:
                if filename.endswith(extension):
                    file_list.append(join(root, filename))
            else:
                file_list.append(join(root, filename))

    return file_list


def create_file_name(path, start):
    """Create the name of rst file.

    Example:
    resources.libraries.python.honeycomb.rst
    tests.perf.rst

    :param path: Path to a module to be documented.
    :param start: The first directory in path which be used in the file name.
    :type path: str
    :type start: str
    :returns: File name.
    :rtype: str
    """
    dir_list = path.split('/')
    start_index = dir_list.index(start)
    return ".".join(dir_list[start_index:-1]) + ".rst"


def create_rst_file_names(files, start):
    """Generate a set of unique rst file names.

    :param files: List of all files to be documented with path beginning in the
    workinf directory.
    :param start: The first directory in path which be used in the file name.
    :type files: list
    :type start: str
    :returns: Set of unique rst file names.
    :rtype: set
    """
    file_names = set()
    for file in files:
        file_names.add(create_file_name(file, start))
    return file_names


def scan_dir(path):
    """Create a list of files and directories in the given directory.

    :param path: Path to the directory.
    :type path: str
    :returns: List of directories and list of files sorted in alphabetical
    order.
    :rtype: tuple of to lists
    """
    files = list()
    dirs = list()
    items = listdir(path)
    for item in items:
        if isfile(join(path, item)) and "__init__" not in item:
            files.append(item)
        elif isdir(join(path, item)):
            dirs.append(item)
    return sorted(dirs), sorted(files)


def write_toc(fh, path, dirs):
    """Write a table of contents to given rst file.

    :param fh: File handler of the rst file.
    :param path: Path to package.
    :param dirs: List of directories to be included in ToC.
    :type fh: file
    :type path: str
    :type dirs: list
    """
    fh.write(rst_toc)
    for dir in dirs:
        fh.write("    {}.{}\n".format('.'.join(path), dir))


def write_module_title(fh, module_name):
    """Write the module title to the given rst file. The title will be on the
    second level.

    :param fh: File handler of the rst file.
    :param module_name: The name of module used for title.
    :type fh: file
    :type module_name: str
    """
    title = "{} module".format(module_name)
    fh.write("\n{}\n{}\n".format(title, '-' * len(title)))


def generate_py_rst_files():
    """Generate all rst files for all python modules."""

    py_libs = get_files(PATH_PY_LIBS, PY_EXT)
    file_names = create_rst_file_names(py_libs, RESOURCES_DIR)

    for file_name in file_names:
        path = join(WORKING_DIR, *file_name.split('.')[:-1])
        dirs, files = scan_dir(path)

        full_path = join(WORKING_DIR, file_name)
        with open(full_path, mode='a') as fh:
            if getsize(full_path) == 0:
                package = file_name.split('.')[-2]
                fh.write("{} package\n".format(package))
                fh.write('=' * len("{} package".format(package)))
            module_path = file_name.split('.')[:-1]
            if dirs:
                write_toc(fh, module_path, dirs)
            for file in files:
                module_name = file.split('.')[0]
                write_module_title(fh, module_name)
                fh.write(rst_py_module.format('.'.join(module_path), module_name))


def generate_rf_rst_files(file_names, incl_tests=True, incl_keywords=True):
    """Generate rst files for the given robot modules.

    :param file_names: List of file name to be included in the documentation
    (rst files).
    :param incl_tests: If true, tests will be included in the documentation.
    :param incl_keywords: If true, keywords will be included in the
    documentation.
    :type file_names: set
    :type incl_tests: bool
    :type incl_keywords: bool
    """

    for file_name in file_names:
        path = join(WORKING_DIR, *file_name.split('.')[:-1])
        dirs, files = scan_dir(path)

        full_path = join(WORKING_DIR, file_name)
        with open(full_path, mode='a') as fh:
            if getsize(full_path) == 0:
                package = file_name.split('.')[-2]
                fh.write("{} package\n".format(package))
                fh.write('=' * len("{} package".format(package)) + '\n')
            module_path = file_name.split('.')[:-1]
            if dirs:
                write_toc(fh, module_path, dirs)
            for file in files:
                module_name = file.split('.')[0]
                write_module_title(fh, module_name)
                path = join(join(*module_path), module_name + RF_EXT)
                if incl_tests:
                    fh.write(rst_rf_tests.format(path))
                if incl_keywords:
                    fh.write(rst_rf_keywords.format(path))


def generate_kw_rst_files():
    """Generate all rst files for all robot modules with keywords in libraries
    directory (no tests)."""

    rf_libs = get_files(PATH_RF_LIBS, RF_EXT)
    file_names = create_rst_file_names(rf_libs, RESOURCES_DIR)

    generate_rf_rst_files(file_names, incl_tests=False)


def generate_tests_rst_files():
    """Generate all rst files for all robot modules with tests in tests
    directory. Include also keywords defined in these modules."""

    tests = get_files(PATH_TESTS, RF_EXT)
    file_names = create_rst_file_names(tests, TESTS_DIR)

    generate_rf_rst_files(file_names)


if __name__ == '__main__':

    # Generate all rst files:
    generate_py_rst_files()
    generate_kw_rst_files()
    generate_tests_rst_files()
