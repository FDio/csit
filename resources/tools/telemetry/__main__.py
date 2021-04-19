#!/usr/bin/env python3

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

"""Telemetry Exporter."""

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .executor import Executor

def main():
    """
    Main entry function when called from cli
    """
    parser = ArgumentParser(
        description=u"Telemetry Exporter.",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        u"-c", u"--config", required=True, type=str,
        help=u"YAML configuration file."
    )
    parser.add_argument(
        u"-p", u"--pid", required=False, type=int,
        help=u"Process ID."
    )
    parser.add_argument(
        u"-d", u"--daemon", required=False, type=bool,
        help=u"Run as daemon."
    )
    args = parser.parse_args()
    if args.daemon:
        Executor(args.config).execute_daemon(args.pid)
    else:
        Executor(args.config).execute(args.pid)

if __name__ == u"__main__":
    main()
