#!/usr/bin/env python

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

"""This script provides copy and load of Docker container images.
   As destinations are used all DUT nodes from the topology file."""

import argparse
from yaml import load

from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error, scp_node


def main():
    """Copy and load of Docker image."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topo", required=True,
                        help="Topology file")
    parser.add_argument("-d", "--directory", required=True,
                        help="Destination directory")
    parser.add_argument("-i", "--images", required=False, nargs='+',
                        help="Images paths to copy")
    parser.add_argument("-c", "--cancel", help="Cancel all",
                        action="store_true")

    args = parser.parse_args()
    topology_file = args.topo
    images = args.images
    directory = args.directory
    cancel_all = args.cancel

    work_file = open(topology_file)
    topology = load(work_file.read())['nodes']

    for node in topology.values():
        if node['type'] == "DUT":
            if cancel_all:
                # Remove destination directory on DUT
                cmd = "rm -fr {directory}".format(directory=directory)
                exec_cmd(node, cmd)
            else:
                # Create installation directory on DUT
                cmd = "rm -rf {directory}; mkdir {directory}"\
                    .format(directory=directory)
                exec_cmd_no_error(node, cmd)

                # Copy images from local path to destination dir
                for image in images:
                    scp_node(node, local_path=image, remote_path=directory)

                # Load image to Docker.
                cmd = "for f in {directory}/*.tar.gz; do "\
                    "docker load -i $f; done >&2".format(directory=directory)
                exec_cmd_no_error(node, cmd, sudo=True)

                # Remove <none> images from Docker.
                cmd = "docker images -f dangling=true -q | xargs -r docker rmi"
                exec_cmd(node, cmd, sudo=True)


if __name__ == "__main__":
    main()
