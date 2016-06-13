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

"""Docker utilities library."""

from time import time

from resources.libraries.python.ssh import exec_cmd, SSH, exec_cmd_no_error


class SetupDocker(object):
    """Docker setup/teardown utilities"""

    @staticmethod
    def check_container_exist(node, container_name):
        """Check whether specific container already exists.

        :param node: Node where to execute command.
        :param container_name: Container name to check.
        :type node: dict
        :type container_name: str
        :return: True in case container exists and vice versa.
        :rtype: bool
        """
        cmd = 'docker ps -a'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        print "Docker info: {}".format(stdout)
        if container_name in stdout:
            return True
        else:
            return False

    @staticmethod
    def install_docker_on_dut(node, timeout=200, sudo=True):
        """!!NOT APPLICABLE FOR AUTOMATED TESTBED!!
        Download and install docker. Usable for local testing.

        :param node: Node where to execute command.
        :param timeout: Download/installation timeout.
        :param sudo: Run with sudo.
        :type node: dict
        :type timeout: int
        :type sudo: bool
        :raises RuntimeError: Installation of docker was not successful.
        :return: Stdout and Stderr.
        :rtype: tuple
        """
        print "Dowloading and installing docker"
        cmd = 'apt-get -y install docker.io'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not install docker, reason:{}'.format(stderr))

        return stdout, stderr

    @staticmethod
    def pull_docker_os(node, timeout=300, sudo=True, os='ubuntu'):
        """!!NOT APPLICABLE FOR AUTOMATED TESTBED!!
        Pull specific image for docker.

        :param node: Node where to execute command.
        :param timeout: Docker image pull timeout.
        :param sudo: Run with sudo.
        :param os: Image to pull.
        :type node: dict
        :type timeout: int
        :type sudo: bool
        :type os: str
        :raises RuntimeError: Pulling of linux image was not successful.
        """
        print "Pulling OS for docker: {}".format(os)
        cmd = 'docker pull {0}'.format(os)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not pull ubuntu docker, reason:{}'.format(stderr))

    @staticmethod
    def create_docker_container_on_dut(node, container_name, cont_active=30000):
        """Start docker container on DUT. If container with given name already
        exists, clean the old one and start a new one.

        :param node: Node where to execute command.
        :param container_name: Name for the new container.
        :param cont_active: Time in seconds for container to stay active.
        :type node: dict
        :type container_name: str
        :type cont_active: int
        """
        print "Creating docker container..."
        if SetupDocker.check_container_exist(node, container_name):
            print "Docker with name {} already exists. \
            Removing old one and setting new.".format(container_name)
            SetupDocker.remove_clean_container(node, container_name)
        ssh = SSH()
        ssh.connect(node)
        cmd = 'sudo -S docker run --name "{}" ubuntu sleep {}'.format(
            container_name, cont_active)
        ssh.exec_command(cmd, background=True)

    @staticmethod
    def connect_container_with_namespace(node, docker_id, timeout=20):
        """Connect running container's pid to namespace.

        :param node: Node where to execute command.
        :param docker_id: Name of the created docker.
        :param timeout: Timeout for obtaining the container's pid.
        :type node: dict
        :type docker_id: str
        :type timeout: int
        :raises RuntimeError: If it is not possible to obtain correct pid ID.
        """
        print "Creating docker container..."
        pid = '{{.State.Pid}}'
        start_time = time()
        while True:
            cmd = 'docker inspect -f {} {}'.format(pid, docker_id)
            (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
            if rc != 0:
                if 'No such image or container' in stderr:
                    continue
                else:
                    raise RuntimeError(
                        'Error :{}'.format(stderr))
            if int(stdout) == 0:
                current_time = time()
                if (current_time - start_time) > timeout:
                    raise RuntimeError(
                        'Could not set correct pid for container: {}'.format(
                            stdout))
            else:
                pid = stdout
                break

        cmd = 'ln -s /proc/{}/ns/net /var/run/netns/{}'.format(
            int(pid), docker_id)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not connect container with namespace, reason:{}'.format(
                    stderr))

    @staticmethod
    def remove_and_clean_all_containers(node):
        """Kill all running containers and subsequently clean the containers
        from docker.

        :param node: Node where to execute command.
        :type node: dict
        :raises RuntimeError: Either the containers were not killed or cleaned.
        """
        print "Stop all running dockers"
        cmd = 'docker kill `sudo -S docker ps --no-trunc -aq`'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=100, sudo=True)
        if rc != 0:
            if 'requires a minimum of 1 argument' in stderr:
                pass
            else:
                raise RuntimeError(
                    'Could not stop containers, reason:{}'.format(stderr))
        print "Stopped successfully: \n{}".format(stdout)
        print "Clean all containers"
        cmd = 'docker rm `sudo -S docker ps --no-trunc -aq`'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=100, sudo=True)
        if rc != 0:
            if 'requires a minimum of 1 argument' in stderr:
                pass
            else:
                raise RuntimeError(
                    'Could not clean containers, reason:{}'.format(stderr))
        print "Cleaned successfully: \n{0}".format(stdout)

    @staticmethod
    def remove_clean_container(node, container_name):
        """Kill specific running container and subsequently clean the container
        from docker.

        :param node: Node where to execute command.
        :param container_name: Container name
        :type node: dict
        :type container_name: str
        """
        cmd = 'docker kill {} && sudo -S docker rm {}'.format(container_name)
        exec_cmd_no_error(node, cmd, sudo=True)
