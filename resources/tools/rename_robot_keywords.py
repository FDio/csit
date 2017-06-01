#!/usr/bin/python

# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""This script renames the given robot keywords in the given directory
recursively.

Example:

  ./rename_robot_keywords.py -i kws.csv -s ";" -d ~/ws/vpp/git/csit/ -vvv

  Input file "kws.csv" is CSV file exported from e.g. MS Excel. Its structure
  must be:

    <Old keyword name><separator><New keyword name>

  One keyword per line.

"""

import argparse
import sys
import re
from os import walk, rename
from os.path import join


def time_interval(func):
    """Decorator function to measure the time spent by the decorated function.

    :param func: Decorated function.
    :type func: Callable object.
    :returns: Wrapper function.
    :rtype: Callable object.
    """

    import time

    def wrapper(*args, **kwargs):
        start = time.clock()
        result = func(*args, **kwargs)
        stop = time.clock()
        print("\nRenaming done in {:.5g} seconds\n".
              format(stop - start))
        return result
    return wrapper


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


def read_keywords(args):
    """This function reads the keywords from the input file and creates:

    - a dictionary where the key is the old name and the value is the new name,
      these keywords will be further processed.
    - a list of keywords which will not be processed, typically keywords with
    argument(s) in its names.
    - a list of duplicates - duplicated keyword names or names which are parts
    of another keyword name, they will not be processed.

    :param args:  Parsed arguments.
    :type args: ArgumentParser
    :returns: keyword names - dictionary where the key is the old name and the
    value is the new name; ignored keyword names - list of keywords which will
    not be processed; duplicates - duplicated keyword names or names which are
    parts of another keyword name, they will not be processed.
    :rtype: tuple(dict, list, list)
    """

    kw_names = dict()
    ignored_kw_names = list()
    duplicates = list()

    for line in args.input:
        old_name, new_name = line.split(args.separator)
        if '$' in old_name:
            ignored_kw_names.append((old_name, new_name[:-1]))
        elif old_name in kw_names.keys():
            duplicates.append((old_name, new_name[:-1]))
        else:
            kw_names[old_name] = new_name[:-1]

    # Remove duplicates:
    for old_name, _ in duplicates:
        new_name = kw_names.pop(old_name, None)
        if new_name:
            duplicates.append((old_name, new_name))

    # Find KW names which are parts of other KW names:
    for old_name in kw_names.keys():
        count = 0
        for key in kw_names.keys():
            if old_name in key:
                count += 1
            if old_name in kw_names[key]:
                if old_name != key:
                    count += 1
        if count > 1:
            duplicates.append((old_name, kw_names[old_name]))
            kw_names.pop(old_name)

    return kw_names, ignored_kw_names, duplicates


def rename_keywords(file_list, kw_names, args):
    """Rename the keywords in specified files.

    :param file_list: List of files to be processed.
    :param kw_names: Dictionary  where the key is the old name and the value is
    the new name
    :type file_list: list
    :type kw_names: dict
    """

    kw_not_found = list()

    for old_name, new_name in kw_names.items():
        kw_found = False
        if args.verbosity > 0:
            print("\nFrom: {}\n  To: {}\n".format(old_name, new_name))
        for file_name in file_list:
            tmp_file_name = file_name + ".new"
            with open(file_name) as file_read:
                file_write = open(tmp_file_name, 'w')
                occurrences = 0
                for line in file_read:
                    new_line = re.sub(old_name, new_name, line)
                    file_write.write(new_line)
                    if new_line != line:
                        occurrences += 1
                if occurrences:
                    kw_found = True
                    if args.verbosity > 1:
                        print(" {:3d}: {}".format(occurrences, file_name))
                file_write.close()
            rename(tmp_file_name, file_name)
        if not kw_found:
            kw_not_found.append(old_name)

    if args.verbosity > 0:
        print("\nKeywords not found:")
        for item in kw_not_found:
            print("  {}".format(item))


def parse_args():
    """Parse arguments from command line.

    :returns: Parsed arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Text file with the old keyword name and the new "
                             "keyword name separated by separator per line.")
    parser.add_argument("-s", "--separator",
                        default=";",
                        type=str,
                        help="Separator which separates the old and the new "
                             "keyword name.")
    parser.add_argument("-d", "--dir",
                        required=True,
                        type=str,
                        help="Directory with robot files where the keywords "
                             "should be recursively searched.")
    parser.add_argument("-v", "--verbosity", action="count",
                        help="Set the output verbosity.")
    return parser.parse_args()


@time_interval
def main():
    """Main function."""

    args = parse_args()

    kw_names, ignored_kw_names, duplicates = read_keywords(args)

    file_list = get_files(args.dir, "robot")

    if args.verbosity > 2:
        print("\nList of files to be processed:")
        for item in file_list:
            print("  {}".format(item))
        print("\n{} files to be processed.\n".format(len(file_list)))

        print("\nList of keywords to be renamed:")
        for item in kw_names:
            print("  {}".format(item))
        print("\n{} keywords to be renamed.\n".format(len(kw_names)))

    rename_keywords(file_list, kw_names, args)

    if args.verbosity >= 0:
        print("\nIgnored keywords: ({})".format(len(ignored_kw_names)))
        for old, new in ignored_kw_names:
            print("  From: {}\n    To: {}\n".format(old, new))

        print("\nIgnored duplicates ({}):".format(len(duplicates)))
        for old, new in duplicates:
            print("  From: {}\n    To: {}\n".format(old, new))


if __name__ == "__main__":
    sys.exit(main())
