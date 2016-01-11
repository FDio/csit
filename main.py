#!/usr/bin/env python

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

"""This is a helper script to make test execution easy."""

from __future__ import print_function
import sys
import os
import time
from string import ascii_lowercase
from random import sample
import argparse
from pykwalify.core import Core
from pykwalify.errors import PyKwalifyException
from yaml import load
import robot
from robot.errors import DATA_ERROR, DataError, FRAMEWORK_ERROR, FrameworkError
from robot.run import RobotFramework
from robot.conf.settings import RobotSettings
from robot.running.builder import TestSuiteBuilder
from robot.running.model import TestSuite

TOPOLOGIES_DIR = './topologies/enabled/'
TESTS_DIR = './tests'
OUTPUTS_DIR = './outputs'


def get_suite_list(*datasources, **options):
    """Returns filtered test suites based on include exclude tags

    :param datasources: paths to tests
    :param options: Robot Framework options (robot.conf.settings.py)
    :return: list of Robot Framework TestSuites which contain tests
    """
    class _MyRobotFramework(RobotFramework):
        """Custom implementation of RobotFramework main()."""
        def main(self, datasources, **options):
            # copied from robot.run.RobotFramework.main
            settings = RobotSettings(options)
            test_suite = TestSuiteBuilder(settings['SuiteNames'],
                                          settings['WarnOnSkipped'])
            # pylint: disable=star-args
            suite = test_suite.build(*datasources)
            suite.configure(**settings.suite_config)

            return suite

    # get all test cases list without run tests, execute runs overloaded main
    # function
    suite = _MyRobotFramework().execute(*datasources, output=None, dryrun=True,
                                        **options)
    if isinstance(suite, TestSuite):
        suites = []
        suites.append(suite)
        append_new = True
        while append_new:
            append_new = False
            tmp = []
            for suite in suites:
                # pylint: disable=protected-access
                if len(suite.suites._items) > 0:
                    for i in suite.suites._items:
                        tmp.append(i)
                    append_new = True
                else:
                    tmp.append(suite)
            suites = tmp
        return suites
        # TODO: check testcases Tags ? all tests should have same set of tags
    else:
        if suite == DATA_ERROR:
            raise DataError
        if suite == FRAMEWORK_ERROR:
            raise FrameworkError
        return []


def run_suites(tests_dir, suites, output_dir, output_prefix='suite',
               **options):
    """Execute RF's run with parameters."""

    with open('{}/{}.out'.format(output_dir, output_prefix), 'w') as out:
        robot.run(tests_dir,
                  suite=[s.longname for s in suites],
                  output='{}/{}.xml'.format(output_dir, output_prefix),
                  debugfile='{}/{}.log'.format(output_dir, output_prefix),
                  log=None,
                  report=None,
                  stdout=out,
                  **options)


def parse_outputs(output_dir):
    """Parse output xmls from all executed tests."""

    outs = [os.path.join(output_dir, file_name)
            for file_name in os.listdir(output_dir)
            if file_name.endswith('.xml')]
    # pylint: disable=star-args
    robot.rebot(*outs, merge=True)


def topology_lookup(topology_paths, topo_dir, validate):
    """Make topology list and validate topologies against schema

    :param parsed_args: topology list, is empty then scans topologies in
                        topo_dir
    :param topo_dir: scan directory for topologies
    :param validate: if True then validate topology
    :return: list of topologies
    """

    ret_topologies = []
    if topology_paths:
        for topo in topology_paths:
            if os.path.exists(topo):
                ret_topologies.append(topo)
            else:
                print("Topology file {} doesn't exist".format(topo),
                      file=sys.stderr)
    else:
        ret_topologies = [os.path.join(topo_dir, file_name)
                          for file_name in os.listdir(topo_dir)
                          if file_name.lower().endswith('.yaml')]

    if len(ret_topologies) == 0:
        print('No valid topology found', file=sys.stderr)
        exit(1)

    # validate topologies against schema
    exit_on_error = False
    for topology_name in ret_topologies:
        try:
            with open(topology_name) as file_name:
                yaml_obj = load(file_name)
            core = Core(source_file=topology_name,
                        schema_files=yaml_obj["metadata"]["schema"])
            core.validate()
        except PyKwalifyException as ex:
            print('Unable to verify topology {}, schema error: {}'.\
                  format(topology_name, ex),
                  file=sys.stderr)
            exit_on_error = True
        except KeyError as ex:
            print('Unable to verify topology {}, key error: {}'.\
                  format(topology_name, ex),
                  file=sys.stderr)
            exit_on_error = True
        except Exception as ex:
            print('Unable to verify topology {}, {}'.format(topology_name, ex),
                  file=sys.stderr)
            exit_on_error = True

    if exit_on_error and validate:
        exit(1)

    return ret_topologies


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='A test runner')
    parser.add_argument('-i', '--include', action='append',
                        help='include tests with tag')
    parser.add_argument('-e', '--exclude', action='append',
                        help='exclude tests with tag')
    parser.add_argument('-s', '--suite', action='append',
                        help='full name of suite to run')
    parser.add_argument('-t', '--topology', action='append',
                        help='topology where tests should be run')
    parser.add_argument('-d', '--test_dir', nargs='?', default=TESTS_DIR,
                        help='where tests are stored')
    parser.add_argument('-o', '--output_dir', nargs='?', default=OUTPUTS_DIR,
                        help='where results are stored')
    parser.add_argument('-L', '--loglevel', nargs='?', default='INFO', type=str,
                        choices=['TRACE', 'DEBUG', 'INFO', 'WARN', 'NONE'],
                        help='robot frameworks level for logging')
    parser.add_argument('-n', '--no_validate', action="store_false",
                        help='Do not exit if topology validation failed')

    args = parser.parse_args()

    i = args.include or []
    excl = args.exclude or []
    suite_filter = args.suite or []
    test_dir = args.test_dir

    # prepare output subdir
    suite_output_dir = os.path.join(args.output_dir,
                                    time.strftime('%y%m%d%H%M%S'))
    os.makedirs(suite_output_dir)

    topologies = topology_lookup(args.topology, TOPOLOGIES_DIR,
                                 args.no_validate)
    suite_list = get_suite_list(test_dir, include=i, exclude=excl,
                                suite=suite_filter)

    # TODO: do the topology suite mapping magic
    #       for now all tests on single topology
    if len(topologies) > 1:
        print('Multiple topologies unsupported yet', file=sys.stderr)
        exit(1)
    topology_suite_mapping = {topologies[0]: suite_list}

    # on all topologies, run test
    # TODO: run parallel
    for topology_path, topology_suite_list in topology_suite_mapping.items():
        topology_path_variable = 'TOPOLOGY_PATH:{}'.format(topology_path)
        variables = [topology_path_variable]
        print('Runing tests on topology {}'.format(topology_path))
        run_suites(test_dir, topology_suite_list, variable=variables,
                   output_dir=suite_output_dir,
                   output_prefix=''.join(sample(ascii_lowercase, 5)),
                   include=i, exclude=excl, loglevel=args.loglevel)

    print('Parsing test results')
    parse_outputs(suite_output_dir)


if __name__ == "__main__":
    main()
