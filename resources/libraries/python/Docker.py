from resources.libraries.python.ssh import exec_cmd, SSH
import resources.libraries.python.ssh

class SetupDocker(object):

    @staticmethod
    def install_docker_on_dut(node, timeout=120, sudo=True):
        print "Dowloading and installing docker"
        cmd = 'apt-get -y install docker.io'
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not install docker, reason:{0}'.format(stderr))


        return stdout, stderr

    @staticmethod
    def pull_docker_os(node, timeout=120, sudo=True, os='ubuntu'):
        print "Pulling OS for docker: {0}".format(os)
        cmd = 'docker pull {0}'.format(os)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=timeout, sudo=sudo)
        if rc != 0:
            raise RuntimeError(
                'Could not pull ubuntu docker, reason:{0}'.format(stderr))

    @staticmethod
    def create_docker_container_on_dut(node, container_name, timeout=5, sudo=True):
        print "Creating docker container..."
        ssh = SSH()
        ssh.connect(node)
        cmd = 'sudo -S docker run --name "{0}" ubuntu sleep 30000'.format(container_name)
        ssh.exec_command(cmd,background=True)

    @staticmethod
    def connect_docker_with_namespace(node, docker_id):
        print "Creating docker container..."
        ssh = SSH()
        ssh.connect(node)
        pid = '{{.State.Pid}}'
        cmd = 'docker inspect -f {0} {1}'.format(pid, docker_id)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))

        cmd = 'ln -s /proc/{0}/ns/net /var/run/netns/{1}'.format(int(stdout), docker_id)
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
    def clean_up(node):
        ssh = SSH()
        ssh.connect(node)
        print "Clean all namespaces"
        cmd = 'rm -Rf /var/run/netns/ && sudo -S mkdir /var/run/netns'
        (rc, stdout, stderr) = ssh.exec_command_sudo(cmd)
        if rc != 0:
            raise RuntimeError('Could not clean namespaces')




