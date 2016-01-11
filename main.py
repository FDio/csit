#!/usr/bin/env python

# TODO: Add Licence

import os
import robot
from robot.run import RobotFramework
from robot.conf.settings import RobotSettings
from robot.running.builder import TestSuiteBuilder
from robot.running.model import TestSuite


def get_suite_list(*datasources, **options):
    class _MyRobotFramework(RobotFramework):
        def main(self, datasources, **options):
            # copied from robot.run.RobotFramework.main
            settings = RobotSettings(options)
            suite = TestSuiteBuilder(settings['SuiteNames'],
                                     settings['WarnOnSkipped']).build(*datasources)
            suite.configure(**settings.suite_config)

            return suite

    # Options are in robot.conf.settings
    suite = _MyRobotFramework().execute(*datasources, **options)
    if isinstance(suite, TestSuite):
        suites = []
        suites.append(suite)
        append_new = True
        while append_new:
            append_new = False
            tmp = []
            for s in suites:
                if len(s.suites._items) > 0:
                    for i in s.suites._items:
                        tmp.append(i)
                    append_new = True
                else:
                    tmp.append(s)
            suites = tmp
        return suites
    else:
        # TODO: add from robot.errors typ error
        return []


def run_suites(test_dir, suites, out_dir="./outputs", **options):
    # TODO: add logic

    try:
        for f in os.listdir(out_dir):
            os.remove('/'.join((out_dir, f)))
    except OSError:
        pass
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for s in suites:
        longname = s.longname
        varfile=[]
        varfile.append('resources/libraries/python/topology.py')

        # TODO: check testcases Tags

        with open('{}/{}.out'.format(out_dir, longname), 'w') as out, \
             open('{}/{}.log'.format(out_dir, longname), 'w') as debug:
            robot.run(test_dir,
                      suite=[longname],
                      output='{}/{}.xml'.format(out_dir, longname),
                      debugfile=debug,
                      log=None,
                      report=None,
                      stdout=out,
                      variablefile=varfile,
                      **options)


def parse_outputs(out_dir='./'):
    outs = ['/'.join((out_dir, file)) for file in os.listdir(out_dir) if file.endswith('.xml')]
    robot.rebot(*outs, merge=True)


if __name__ == "__main__":
    i = []
    e = []
    # i = ['bd', 'ip']
    # i = ['hw']
    # e = ['hw']
    test_dir = "./tests"
    out_dir = "./outputs"

    suite_list = get_suite_list(test_dir, include=i, exclude=e, output=None, dryrun=True)
    run_suites(test_dir, suite_list, include=i, exclude=e, out_dir=out_dir)
    parse_outputs(out_dir=out_dir)
