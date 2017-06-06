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

"""Library to manipulate LXC."""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType


__all__ = ["LXCUtils"]

class LXCUtils(object):
    """LXC utilities."""

    def __init__(self, container_name='slave'):
        # LXC container name
        self._container_name = container_name
        self._node = None
        # Host hugepages dir that will be mounted inside LXC
        self._host_hugepages_dir = '/dev/hugepages'
        # Host dir that will be mounted inside LXC
        self._host_dir = '/tmp/'
        # Guest dir to mount host dir to
        self._guest_dir = '/mnt/host'
        # LXC container env variables
        self._env_vars = ['LC_ALL="en_US.UTF-8"',
                          'DEBIAN_FRONTEND=noninteractive']

    def set_node(self, node):
        """Set node for LXC execution.

        :param node: Node to execute LXC on.
        :type node: dict
        :raises RuntimeError: If Node type is not DUT.
        """
        if node['type'] != NodeType.DUT:
            raise RuntimeError('Node type is not DUT.')
        self._node = node

    def set_host_dir(self, node, host_dir):
        """Set shared dir on parent node for LXC.

        :param node: Node to control LXC on.
        :type node: dict
        :raises RuntimeError: If Node type is not DUT.
        """
        if node['type'] != NodeType.DUT:
            raise RuntimeError('Node type is not DUT.')
        self._host_dir = host_dir

    def set_guest_dir(self, node, guest_dir):
        """Set mount dir on LXC.

        :param node: Node to control LXC on.
        :param guest_dir: Guest dir for mount.
        :type node: dict
        :type guest_dir: str
        :raises RuntimeError: If Node type is not DUT.
        """
        if node['type'] != NodeType.DUT:
            raise RuntimeError('Node type is not DUT.')
        self._guest_dir = guest_dir

    def _lxc_checkconfig(self):
        """Check the current kernel for LXC support.

        :raises RuntimeError: If failed to check LXC support.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo('lxc-checkconfig')
        if int(ret) != 0:
            raise RuntimeError('Failed to check LXC support.')

    def _lxc_create(self, distro='ubuntu', release='xenial', arch='amd64'):
        """Creates a privileged system object where is stored the configuration
        information and where can be stored user information.

        :param distro: Linux distribution name.
        :param release: Linux distribution release.
        :param arch: Linux distribution architecture.
        :type distro: str
        :type release: str
        :type arch: str
        :raises RuntimeError: If failed to create a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-create -t download --name {0} -- -d {1} -r {2} -a {3}'
            .format(self._container_name, distro, release, arch), timeout=1800)
        if int(ret) != 0:
            raise RuntimeError('Failed to create LXC container.')

    def _lxc_info(self):
        """Queries and shows information about a container.

        :raises RuntimeError: If failed to get info about a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-info --name {0}'.format(self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about LXC container {0}.'
                               .format(self._container_name))

    def _lxc_start(self):
        """Start an application inside a container.

        :raises RuntimeError: If failed to start container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-start --name {0} --daemon'.format(self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to start LXC container {0}.'
                               .format(self._container_name))

    def _lxc_stop(self):
        """Stop an application inside a container.

        :raises RuntimeError: If failed to stop container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-stop --name {0}'.format(self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to stop LXC container {}.'
                               .format(self._container_name))

    def _lxc_destroy(self):
        """Destroy a container.

        :raises RuntimeError: If failed to destroy container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-destroy --force --name {0}'.format(self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to destroy LXC container {}.'
                               .format(self._container_name))

    def _lxc_wait(self, state):
        """Wait for a specific container state.

        :param state: Specify the container state(s) to wait for.
        :type state: str
        :raises RuntimeError: If failed to wait for state of a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-wait --name {0} --state "{1}"'
            .format(self._container_name, state))
        if int(ret) != 0:
            raise RuntimeError('Failed to wait for "{0}" of LXC container {1}.'
                               .format(state, self._container_name))

    def _lxc_cgroup(self, state_object, value=''):
        """Manage the control group associated with a container.

        :param state_object: Specify the state object name.
        :param value: Specify the value to assign to the state object. If empty,
        then action is GET, otherwise is action SET.
        :type state_object: str
        :type value: str
        :raises RuntimeError: If failed to get/set for state of a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-cgroup --name {0} {1} {2}'
            .format(self._container_name, state_object, value))
        if int(ret) != 0:
            if value:
                raise RuntimeError('Failed to set {0} of LXC container {1}.'
                                   .format(state_object, self._container_name))
            else:
                raise RuntimeError('Failed to get {0} of LXC container {1}.'
                                   .format(state_object, self._container_name))

    def lxc_attach(self, command):
        """Start a process inside a running container. Runs the specified
        command inside the container specified by name. The container has to
        be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If container is not running.
        :raises RuntimeError: If failed to run the command.
        """
        env_var = '--keep-env {0}'\
            .format(' '.join('--set-var %s' % var for var in self._env_vars))

        ssh = SSH()
        ssh.connect(self._node)

        if not self.is_container_running():
            raise RuntimeError('LXC {0} is not running.'
                               .format(self._container_name))

        ret, _, _ = ssh.exec_command_lxc(lxc_cmd=command,
                                         lxc_name=self._container_name,
                                         lxc_params=env_var, timeout=180)
        if int(ret) != 0:
            raise RuntimeError('Failed to run "{0}" on LXC container {1}.'
                               .format(command, self._container_name))

    def is_container_present(self):
        """Check if LXC container is existing on node."""

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo(
            'lxc-info --name {0}'.format(self._container_name))
        return False if int(ret) else True

    def create_container(self, force_create=True):
        """Create and start a container.

        :param force_create: Destroy a container if exists and create.
        :type force_create: bool
        """
        if self.is_container_present():
            if force_create:
                self.destroy_container()
            else:
                return

        self._lxc_checkconfig()
        self._lxc_create(distro='ubuntu', release='xenial', arch='amd64')
        self.start_container()

    def start_container(self):
        """Start a container and wait for running state."""

        self._lxc_start()
        self._lxc_wait('RUNNING')
        self._lxc_info()

    def is_container_running(self):
        """Check if LXC container is running on node.

        :raises RuntimeError: If failed to get info about a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, stdout, _ = ssh.exec_command_sudo(
            'lxc-info --state --name {0}'.format(self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about LXC container {0}.'
                               .format(self._container_name))

        return True if 'RUNNING' in stdout else False

    def stop_container(self):
        """Stop a container and wait for stopped state."""

        self._lxc_stop()
        self._lxc_wait('STOPPED|FROZEN')
        self._lxc_info()

    def restart_container(self):
        """Restart container."""

        self.stop_container()
        self.start_container()

    def destroy_container(self):
        """Stop and destroy a container."""

        self._lxc_destroy()

    def container_cpuset_cpus(self, container_cpu):
        """Set cpuset.cpus control group associated with a container.

        :param container_cpu: Cpuset.cpus string.
        :type container_cpu: str
        :raises RuntimeError: If failed to set cgroup for a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        ret, _, _ = ssh.exec_command_sudo('cgset --copy-from / lxc')
        if int(ret) != 0:
            raise RuntimeError('Failed to copy cgroup settings from root.')

        self._lxc_cgroup(state_object='cpuset.cpus')
        self._lxc_cgroup(state_object='cpuset.cpus', value=container_cpu)
        self._lxc_cgroup(state_object='cpuset.cpus')

    def mount_host_dir_in_container(self):
        """Mount shared folder inside container.

        :raises RuntimeError: If failed to mount host dir in a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        mnt_cfg = 'lxc.mount.entry = {0} /var/lib/lxc/{1}/rootfs{2} ' \
            'none bind,create=dir 0 0'.format(self._host_dir,
                                              self._container_name,
                                              self._guest_dir)
        ret, _, _ = ssh.exec_command_sudo(
            "sh -c 'echo \"{0}\" >> /var/lib/lxc/{1}/config'"
            .format(mnt_cfg, self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to mount {0} in lxc: {1}'
                               .format(self._host_dir, self._container_name))

        self.restart_container()

    def mount_hugepages_in_container(self):
        """Mount hugepages inside container.

        :raises RuntimeError: If failed to mount hugepages in a container.
        """

        ssh = SSH()
        ssh.connect(self._node)

        mnt_cfg = 'lxc.mount.entry = {0} dev/hugepages ' \
            'none bind,create=dir 0 0'.format(self._host_hugepages_dir)
        ret, _, _ = ssh.exec_command_sudo(
            "sh -c 'echo \"{0}\" >> /var/lib/lxc/{1}/config'"
            .format(mnt_cfg, self._container_name))
        if int(ret) != 0:
            raise RuntimeError('Failed to mount {0} in lxc: {1}'
                               .format(self._host_hugepages_dir,
                                       self._container_name))

        self.restart_container()

    def install_vpp_in_container(self, install_dkms=False):
        """Install vpp inside a container.

        :param install_dkms: If install dkms package. This will impact install
        time. Dkms is required for installation of vpp-dpdk-dkms. Default is
        false.
        :type install_dkms: bool
        """

        ssh = SSH()
        ssh.connect(self._node)

        self.lxc_attach('apt-get update')
        if install_dkms:
            self.lxc_attach('apt-get install -y dkms && '
                            'dpkg -i --force-all {0}/install_dir/*.deb'
                            .format(self._guest_dir))
        else:
            self.lxc_attach('for i in $(ls -I \"*dkms*\" {0}/install_dir/); '
                            'do dpkg -i --force-all {0}/install_dir/$i; done'
                            .format(self._guest_dir))
        self.lxc_attach('apt-get -f install -y')

    def restart_vpp_in_container(self):
        """Restart vpp service inside a container."""

        ssh = SSH()
        ssh.connect(self._node)

        self.lxc_attach('service vpp restart')

    def create_vpp_cfg_in_container(self, vat_template_file, **args):
        """Create VPP exec config for a container on given node.

        :param vat_template_file: Template file name of a VAT script.
        :param args: Dictionary of parameters for VAT script.
        :type vat_template_file: str
        :type args: list
        :return: nothing
        """
        ssh = SSH()
        ssh.connect(self._node)

        vat_file_path = '{}/{}'.format(Constants.RESOURCES_TPL_VAT,
                                       vat_template_file)

        with open(vat_file_path, 'r') as template_file:
            cmd_template = template_file.readlines()
            for line_tmpl in cmd_template:
                vat_cmd = line_tmpl.format(**args)
                ssh.exec_command('echo "{0}" | '
                                 'sudo lxc-attach --name {1} -- '
                                 '/bin/sh -c "/bin/cat >> /tmp/running.exec"'
                                 .format(vat_cmd.replace('\n', ''),
                                         self._container_name))
