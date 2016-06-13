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

from time import time

from resources.libraries.python.ssh import exec_cmd, SSH, exec_cmd_no_error


class SetupDocker(object):

    @staticmethod
    def check_docker_exist(node, docker_name):
        cmd = 'docker ps -a'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        print "Docker info: {0}".format(stdout)
        if docker_name in stdout:
            return True
        else:
            return False

    @staticmethod
    def install_docker_on_dut(node, timeout=200, sudo=True):
        print "Dowloading and installing docker"
        cmd = 'apt-get -y install docker.io'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not install docker, reason:{0}'.format(stderr))


        return stdout, stderr

    @staticmethod
    def pull_docker_os(node, timeout=300, sudo=True, os='ubuntu'):
        print "Pulling OS for docker: {0}".format(os)
        cmd = 'docker pull {0}'.format(os)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not pull ubuntu docker, reason:{0}'.format(stderr))

    @staticmethod
    def create_docker_container_on_dut(node, container_name, timeout=5, sudo=True):
        print "Creating docker container..."
        if SetupDocker.check_docker_exist(node, container_name):
            print "Docker with name {0} already exists. Removing old one and setting new.".format(container_name)
            SetupDocker.remove_clean_container(node, container_name)
        ssh = SSH()
        ssh.connect(node)
        cmd = 'sudo -S docker run --name "{0}" ubuntu sleep 30000'.format(container_name)
        ssh.exec_command(cmd,background=True)

    @staticmethod
    def connect_docker_with_namespace(node, docker_id, timeout=20):
        print "Creating docker container..."
        ssh = SSH()
        ssh.connect(node)
        pid = '{{.State.Pid}}'
        start_time = time()
        while True:
            cmd = 'docker inspect -f {0} {1}'.format(pid, docker_id)
            (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
            if rc != 0:
                if 'No such image or container' in stderr:
                    continue
                else:
                    raise RuntimeError(
                        'Could not..., reason:{0}'.format(stderr))
            if int(stdout) == 0:
                current_time = time()
                if (current_time - start_time) > timeout:
                    raise RuntimeError('Could not set correct pid for container: {0}'.format(stdout))
            else:
                pid = stdout
                break

        cmd = 'ln -s /proc/{0}/ns/net /var/run/netns/{1}'.format(int(pid), docker_id)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))

    @staticmethod
    def remove_and_clean_all_dockers(node):
        ssh = SSH()
        ssh.connect(node)
        print "Stop all running dockers"
        cmd = 'docker kill `sudo -S docker ps --no-trunc -aq`'
        (rc, stdout, stderr) = ssh.exec_command_sudo(cmd, timeout=100)
        if rc != 0:
            if 'requires a minimum of 1 argument' in stderr:
                pass
            else:
                raise RuntimeError(
                    'Could not stop docker containers, reason:{0}'.format(stderr))
        print "Stopped successfully: \n{0}".format(stdout)
        print "Clean all containers"
        cmd = 'docker rm `sudo -S docker ps --no-trunc -aq`'
        (rc, stdout, stderr) = ssh.exec_command_sudo(cmd, timeout=100)
        if rc != 0:
            if 'requires a minimum of 1 argument' in stderr:
                pass
            else:
                raise RuntimeError(
                    'Could not clean docker containers, reason:{0}'.format(stderr))
        print "Cleaned successfully: \n{0}".format(stdout)

    @staticmethod
    def remove_clean_container(node, container_name):
        cmd = 'docker kill {0} && sudo -S docker rm {0}'.format(container_name)
        exec_cmd_no_error(node, cmd, sudo=True)


