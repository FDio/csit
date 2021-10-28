# Copyright (c) 2021 Cisco and/or its affiliates.
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
from os import walk, listdir, scandir, environ
from os.path import isfile, isdir, join, getsize

# Temporary working directory. It is created and deleted by docs.sh
WORKING_DIR = environ.get("WORKING_DIR")

# Directory with resources to be documented.
RESOURCES_DIR = u"resources"

# Directory with libraries (python, robot) to be documented.
LIB_DIR = u"libraries"

# Directory with tests (func, perf) to be documented.
TESTS_DIR = u"tests"

PY_EXT = u".py"
RF_EXT = u".robot"

PATH_PY_LIBS = join(WORKING_DIR, RESOURCES_DIR, LIB_DIR, u"python")
PATH_RF_LIBS = join(WORKING_DIR, RESOURCES_DIR, LIB_DIR, u"robot")
PATH_TESTS = join(WORKING_DIR, TESTS_DIR)

# Sections in rst files
rst_toc = u"""
.. toctree::
"""

rst_py_module = u"""
.. automodule:: {}.{}
    :members:
    :undoc-members:
    :show-inheritance:
"""

rst_rf_suite_setup = u"""
.. robot-settings::
   :source: {}
"""

rst_rf_variables = u"""
.. robot-variables::
   :source: {}
"""

rst_rf_keywords = u"""
.. robot-keywords::
   :source: {}
"""

rst_rf_tests = u"""
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
                if filename.endswith(extension) and u"__init__" not in filename:
                    file_list.append(join(root, filename))
            else:
                file_list.append(join(root, filename))

    return file_list


def create_file_name(path, start):
    """Create the name of rst file.

    Example:
    tests.perf.rst

    :param path: Path to a module to be documented.
    :param start: The first directory in path which is used in the file name.
    :type path: str
    :type start: str
    :returns: File name.
    :rtype: str
    """
    dir_list = path.split(u"/")
    start_index = dir_list.index(start)
    return u".".join(dir_list[start_index:-1]) + u".rst"


def create_rst_file_names_set(files, start):
    """Generate a set of unique rst file names.

    :param files: List of all files to be documented with path beginning in the
    working directory.
    :param start: The first directory in path which is used in the file name.
    :type files: list
    :type start: str
    :returns: Set of unique rst file names.
    :rtype: set
    """
    file_names = set()
    for file in files:
        file_names.add(create_file_name(file, start))
    return file_names


def add_nested_folders_in_rst_set(file_names, path):
    """Add RST files from folders where are only folders without tests.

    :param file_names: List of all files to be documented with path beginning
        in the working directory.
    :param path: Path where it starts adding missing RST files.
    :type file_names: list
    :type path: str
    """

    # When we split directory tree by "/" we don't need to create RST file in
    # folders in depth <= 5. It's because the WORKING_DIR folder structure i
    # as following:
    # /tmp/tmp-csitXXX/tests/<subject_of_test>/<type_of_test>/<what_is_tested>
    # That splits to ie:
    # ['', 'tmp', 'tmp-csitXXX', 'tests', 'vpp', 'device', 'container_memif']
    # We need to generate RST files for folders after <subject_of_test> which
    # is in depth > 5

    for directory in fast_scandir(path):
        dir_list = directory.split(u"/")
        if len(dir_list) > 5:
            # cut ['', 'tmp', 'tmp-csitXXX']
            dir_rst = u".".join(dir_list[3:]) + u".rst"
            if dir_rst not in file_names and u"__pycache__" not in dir_rst:
                file_names.add(dir_rst)


def scan_dir(path):
    """Create a list of files and directories in the given directory.

    :param path: Path to the directory.
    :type path: str
    :returns: List of directories and list of files sorted in alphabetical
    order.
    :rtype: tuple of two lists
    """
    files = list()
    dirs = list()
    items = listdir(path)
    for item in items:
        if isfile(join(path, item)) and u"__init__" not in item:
            files.append(item)
        elif isdir(join(path, item)):
            dirs.append(item)
    return sorted(dirs), sorted(files)


def write_toc(fh, path, dirs):
    """Write a table of contents to given rst file.

    :param fh: File handler of the rst file.
    :param path: Path to package.
    :param dirs: List of directories to be included in ToC.
    :type fh: BinaryIO
    :type path: str
    :type dirs: list
    """
    fh.write(rst_toc)
    for directory in dirs:
        fh.write(f"    {u'.'.join(path)}.{directory}\n")


def write_module_title(fh, module_name):
    """Write the module title to the given rst file. The title will be on the
    second level.

    :param fh: File handler of the rst file.
    :param module_name: The name of module used for title.
    :type fh: BinaryIO
    :type module_name: str
    """
    title = f"{module_name} suite"
    fh.write(f"\n{title}\n{u'-' * len(title)}")


def generate_py_rst_files():
    """Generate all rst files for all python modules."""

    dirs_ignore_list = [u"__pycache__", ]

    py_libs = get_files(PATH_PY_LIBS, PY_EXT)
    file_names = create_rst_file_names_set(py_libs, RESOURCES_DIR)

    for file_name in file_names:
        path = join(WORKING_DIR, *file_name.split(u".")[:-1])
        dirs, files = scan_dir(path)

        for item in dirs_ignore_list:
            while True:
                try:
                    dirs.remove(item)
                except ValueError:
                    break

        full_path = join(WORKING_DIR, file_name)
        with open(full_path, mode="a") as fh:
            if getsize(full_path) == 0:
                package = file_name.split(u".")[-2]
                fh.write(f"{package}\n")
                fh.write(u"=" * len(f"{package}"))
            module_path = file_name.split(u".")[:-1]
            if dirs:
                write_toc(fh, module_path, dirs)
            for file in files:
                module_name = file.split(u".")[0]
                write_module_title(fh, module_name)
                fh.write(rst_py_module.format(
                    u".".join(module_path), module_name)
                )


def generate_rf_rst_files(
        file_names, incl_tests=True, incl_keywords=True, incl_suite_setup=False,
        incl_variables=False):
    """Generate rst files for the given robot modules.

    :param file_names: List of file names to be included in the documentation
    (rst files).
    :param incl_tests: If True, tests will be included in the documentation.
    :param incl_keywords: If True, keywords will be included in the
    documentation.
    :param incl_suite_setup: If True, the suite setup will be included in the
    documentation.
    :param incl_variables: If True, the variables will be included in the
    documentation.
    :type file_names: set
    :type incl_tests: bool
    :type incl_keywords: bool
    :type incl_suite_setup: bool
    :type incl_variables: bool
    """

    for file_name in file_names:
        path = join(WORKING_DIR, *file_name.split(u".")[:-1])
        dirs, files = scan_dir(path)

        full_path = join(WORKING_DIR, file_name)
        with open(full_path, mode="a") as fh:
            if getsize(full_path) == 0:
                package = file_name.split(u".")[-2]
                fh.write(f"{package}\n")
                fh.write(u"=" * len(f"{package}") + u"\n")
            module_path = file_name.split(u".")[:-1]
            if dirs:
                write_toc(fh, module_path, dirs)
            for file in files:
                module_name = file.split(u".")[0]
                write_module_title(fh, module_name)
                path = join(join(*module_path), module_name + RF_EXT)
                if incl_suite_setup:
                    fh.write(rst_rf_suite_setup.format(path))
                if incl_variables:
                    fh.write(rst_rf_variables.format(path))
                if incl_keywords:
                    fh.write(rst_rf_keywords.format(path))
                if incl_tests:
                    fh.write(rst_rf_tests.format(path))


def generate_kw_rst_files():
    """Generate all rst files for all robot modules with keywords in libraries
    directory (no tests)."""

    rf_libs = get_files(PATH_RF_LIBS, RF_EXT)
    file_names = create_rst_file_names_set(rf_libs, RESOURCES_DIR)

    generate_rf_rst_files(file_names, incl_tests=False)


def generate_tests_rst_files():
    """Generate all rst files for all robot modules with tests in tests
    directory. Include also keywords defined in these modules."""

    tests = get_files(PATH_TESTS, RF_EXT)
    file_names = create_rst_file_names_set(tests, TESTS_DIR)
    add_nested_folders_in_rst_set(file_names, PATH_TESTS)

    generate_rf_rst_files(
        file_names, incl_suite_setup=True, incl_variables=True
    )
    for test in tests:
        with open(test, 'r') as f:
            newlines = []
            write = False
            for line in f.readlines():
                if u"| Documentation" in line and not write:
                    write = True
                elif u"***" in line and write:
                    write = False
                    newlines.append(u'\n\n')
                if write:
                    newlines.append(line.replace(u'*[', u'\n| ... | - *[')
                                    .replace(u"*", u"**"))
                else:
                    newlines.append(line)
        with open(test, 'w') as f:
            for line in newlines:
                f.write(line)

def fast_scandir(dirname):
    subfolders = [f.path for f in scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


if __name__ == u"__main__":

    # Generate all rst files:
    generate_py_rst_files()
    generate_kw_rst_files()
    generate_tests_rst_files()
