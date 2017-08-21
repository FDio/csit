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

# Bug workaround in pylint for abstract classes.
#pylint: disable=W0223
#pylint: disable=E1101

"""Library to manipulate with Containers."""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator

from collections import OrderedDict


__all__ = ["ContainerManager", "ContainerEngine", "LXC", "Docker", "Container"]

SUPERVISOR_CONF = '/etc/supervisord.conf'

class ContainerManager(object):
    """Container orchestration class."""

    def __init__(self, engine):
        """Initialize Container Manager class.

        :param engine: Container techology used (LXC/Docker/...).
        :type engine: str
        :raises NotImplementedError: If container engine is not implemented.
        """

        try:
            self.engine = globals()[engine]()
        except KeyError:
            raise NotImplementedError('Container engine not implemented.')
        self.containers = OrderedDict()

    def get_container_by_name(self, name):
        """Get container instance.

        :param name: Container name.
        :type name: str
        :returns: Container instance.
        :rtype: Container
        :raises RuntimeError: If failed to get contatiner with name.
        """

        try:
            return self.containers[name]
        except KeyError:
            raise RuntimeError('Failed to get conatiner with name: {n}'
                               .format(n=name))

    def construct_container(self, **kwargs):
        """Create 1..N container(s) on node with specified name.
        Ordinal number is automatically added to the name of container as
        suffix.

        :param kwargs: Key-value pairs used to create container.
        :param kwargs: dict
        """

        for i in range(kwargs['count']):
            # Name will contain ordinal suffix
            name = ''.join([kwargs['name'], str(i)])
            # Create base class
            self.engine.init(kwargs['node'], name)
            # Print system info
            self.engine.system_info()
            # Set container image specification
            self.engine.container.image_spec = kwargs['image']
            # Set label to identify container instance
            self.engine.container.env = ('MICROSERVICE_LABEL={0}'
                                         .format(name))
            # Set cpuset.cpus cgroup
            if kwargs['cpu_shared']:
                self.engine.container.cpuset_cpus = \
                    CpuUtils.cpu_slice_of_list_per_node(
                        node=kwargs['node'], cpu_node=kwargs['cpu_node'],
                        skip_cnt=kwargs['skip_cnt'], cpu_cnt=kwargs['cpu_cnt'],
                        smt_used=kwargs['smt_used'])
            else:
                skip = kwargs['skip_cnt'] + i * kwargs['cpu_cnt']
                self.engine.container.cpuset_cpus = \
                    CpuUtils.cpu_slice_of_list_per_node(
                        node=kwargs['node'], cpu_node=kwargs['cpu_node'],
                        skip_cnt=skip, cpu_cnt=kwargs['cpu_cnt'],
                        smt_used=kwargs['smt_used'])
            # Set cpuset.mems cgroup
            self.engine.container.cpuset_mems = kwargs['cpu_node']
            # Create (download/pull) container
            self.engine.create()

            # Store container instance
            self.containers[name] = self.engine.container

    def start_all_containers(self):
        """Start all stored containers."""

        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.start()

    def install_vpp_in_all_containers(self):
        """Start all stored containers with vpp instance."""

        for container in self.containers:
            self.engine.container = self.containers[container]
            # We need to install supervisor client/server system to control VPP
            # as a service
            self.engine.install_supervisor()
            self.engine.install_vpp()
            self.engine.create_vpp_startup_config()
            self.engine.create_vpp_exec_config('memif_create_lxc.vat',
                                               socket1='memif-{c.name}-1'
                                               .format(c=self.engine.container),
                                               socket2='memif-{c.name}-2'
                                               .format(c=self.engine.container))
            self.engine.restart_vpp()

    def stop_all_containers(self):
        """Stop all stored containers."""

        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.stop()

    def destroy_all_containers(self):
        """Destroy all stored containers."""

        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.destroy()

    def execute_on_container(self, name, command):
        """Execute command on container with name.

        :param name: Container name.
        :param command: Command to execute.
        :type name: str
        :type command: str
        """

        self.engine.container = self.get_container_by_name(name)
        self.engine.execute(command)

    def execute_on_all_containers(self, command):
        """Execute command on all containers.i

        :param command: Command to execute.
        :type command: str
        """

        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.execute(command)


class ContainerEngine(object):
    """Abstract class for container engine."""

    def __init__(self):
        # Specific container engine instance
        self.container = None

    def init(self, node, name):
        """Initialize container object.

        :param node: DUT node to run container on.
        :param name: Container name.
        :type node: dict
        :type name: str
        """

        self.container = Container(node, name)

    def create(self, force_create):
        """Create/download container."""

        raise NotImplementedError

    def start(self):
        """Start container."""

        raise NotImplementedError

    def stop(self):
        """Stop container."""

        raise NotImplementedError

    def destroy(self):
        """Destroy/remove container."""

        raise NotImplementedError

    def info(self):
        """Info about container."""

        raise NotImplementedError

    def execute(self, command):
        """Execute process inside container."""

        raise NotImplementedError

    def system_info(self):
        """System info."""

        raise NotImplementedError

    def install_supervisor(self):
        """Install supervisord inside a container."""

        self.execute('apt-get update')
        self.execute('apt-get install -y supervisor')
        self.execute('echo "{0}" > {1}'
                     .format(\
                        '[unix_http_server]\n'
                        'file  = /tmp/supervisor.sock\n'
                        '[rpcinterface:supervisor]\n'
                        'supervisor.rpcinterface_factory = '
                        'supervisor.rpcinterface:make_main_rpcinterface\n'
                        '[supervisorctl]\n'
                        'serverurl = unix:///tmp/supervisor.sock\n'
                        '[supervisord]\n'
                        'pidfile = /tmp/supervisord.pid\n'
                        'identifier = supervisor\n'
                        'directory = /tmp\n'
                        'logfile=/tmp/supervisord.log\n'
                        'loglevel=debug\n'
                        'nodaemon=false\n',
                        SUPERVISOR_CONF))
        self.execute('supervisord -c {0}'.format(SUPERVISOR_CONF))

    def install_vpp(self, install_dkms=False):
        """Install vpp inside a container.

        :param install_dkms: If install dkms package. This will impact install
        time. Dkms is required for installation of vpp-dpdk-dkms. Default is
        false.
        :type install_dkms: bool
        """

        self.execute('apt-get update')
        if install_dkms:
            self.execute('apt-get install -y dkms && '
                         'dpkg -i --force-all {0}/install_dir/*.deb'
                         .format(self.container.guest_dir))
        else:
            self.execute('for i in $(ls -I \"*dkms*\" {0}/install_dir/); '
                         'do dpkg -i --force-all {0}/install_dir/$i; done'
                         .format(self.container.guest_dir))
        self.execute('apt-get -f install -y')
        self.execute('echo "{0}" >> {1}'
                     .format(\
                        '[program:vpp]\n'
                        'command=/usr/bin/vpp -c /etc/vpp/startup.conf\n'
                        'autorestart=false\n'
                        'redirect_stderr=true\n'
                        'priority=1',
                        SUPERVISOR_CONF))
        self.execute('supervisorctl reload')

    def restart_vpp(self):
        """Restart vpp service inside a container."""

        self.execute('supervisorctl restart vpp')

    def create_vpp_startup_config(self,
                                  config_filename='/etc/vpp/startup.conf'):
        """Create base startup configuration of VPP on container.

        :param config_filename: Startup configuration file name.
        :type config_filename: str
        """

        cpuset_cpus = self.container.cpuset_cpus

        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self.container.node)
        vpp_config.set_config_filename(config_filename)
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_nodaemon()
        vpp_config.add_unix_exec('/tmp/running.exec')
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_cpus.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = ','.join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.add_plugin_disable('dpdk_plugin.so')

        self.execute('echo "{0}" | tee {1}'\
            .format(vpp_config.get_config_str(),
                    vpp_config.get_config_filename()))

    def create_vpp_exec_config(self, vat_template_file, **args):
        """Create VPP exec configuration on container.

        :param vat_template_file: Template file name of a VAT script.
        :param args: Parameters for VAT script.
        :type vat_template_file: str
        :type args: dict
        """

        vat_file_path = '{}/{}'.format(Constants.RESOURCES_TPL_VAT,
                                       vat_template_file)

        with open(vat_file_path, 'r') as template_file:
            cmd_template = template_file.readlines()
            for line_tmpl in cmd_template:
                vat_cmd = line_tmpl.format(**args)
                self.execute('echo "{0}" >> /tmp/running.exec'
                             .format(vat_cmd.replace('\n', ''),
                                     c=self.container))

    def is_container_running(self):
        """Check if container is running."""

        raise NotImplementedError

    def is_container_present(self):
        """Check if container is present."""

        raise NotImplementedError


class LXC(ContainerEngine):
    """Linux LXC implementation."""

    def create(self, force_create=True):
        """Creates a privileged system object where is stored the configuration
        information and where can be stored user information.

        :param force_create: Destroy a container if exists and create.
        :type force_create: bool
        :raises RuntimeError: If failed to create a container.
        """
        if self.is_container_present():
            if force_create:
                self.destroy()
            else:
                return

        cmd = 'lxc-create -t download --name {c.name} -- {c.image_spec} '\
            '--no-validate'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
        if int(ret) != 0:
            raise RuntimeError('Failed to create container.')

        entry = 'lxc.mount.entry = '\
            '{c.host_dir} /var/lib/lxc/{c.name}/rootfs{c.guest_dir} ' \
            'none bind,create=dir 0 0'.format(c=self.container)
        ret, _, _ = self.container.ssh.exec_command_sudo(
            "sh -c 'echo \"{e}\" >> /var/lib/lxc/{c.name}/config'"
            .format(e=entry, c=self.container))
        if int(ret) != 0:
            raise RuntimeError('Failed to mount {c.host_dir} in: {c.name}'
                               .format(c=self.container))

    def start(self):
        """Start an application inside a container.

        :raises RuntimeError: If failed to start container.
        """
        cmd = 'lxc-start --name {c.name} --daemon'.format(c=self.container)
        cpuset_cpus = ','.join(str(cpu) for cpu in self.container.cpuset_cpus)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to start container {c.name}'
                               .format(c=self.container))
        self._lxc_wait('RUNNING')
        self._lxc_cgroup(state_object='cpuset.cpus',
                         value=cpuset_cpus)

    def stop(self):
        """Stop an application running inside a container.

        :raises RuntimeError: If failed to stop application in a container.
        """
        cmd = 'lxc-stop --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to stop container {c.name}.'
                               .format(c=self.container))
        self._lxc_wait('STOPPED|FROZEN')

    def destroy(self):
        """Destroy a container.

        :raises RuntimeError: If failed to destroy container.
        """
        cmd = 'lxc-destroy --force --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to destroy LXC container {c.name}.'
                               .format(c=self.container))

    def info(self):
        """Queries and shows information about a container.

        :raises RuntimeError: If failed to get info about a container.
        """
        cmd = 'lxc-info --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'\
                               .format(c=self.container))

    def execute(self, command):
        """Start a process inside a running container. Runs the specified
        command inside the container specified by name. The container has to
        be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If failed to run the command.
        """
        env_var = '--keep-env {0}'.format(' '\
            .join('--set-var %s' % var for var in self.container.env))

        cmd = "lxc-attach {e} --name {c.name} -- /bin/sh -c '{k}'"\
            .format(e=env_var, c=self.container, k=command)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError('Failed to run "{k}" inside container {c.name}.'
                               .format(k=command, c=self.container))

    def system_info(self):
        """Check the current kernel for LXC support.

        :raises RuntimeError: If failed to check LXC support.
        """
        cmd = 'lxc-checkconfig'

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to check LXC support.')

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        :raises RuntimeError: If failed to get info about a container.
        """
        cmd = 'lxc-info --no-humanize --state --name {c.name}'\
            .format(c=self.container)

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))
        return True if 'RUNNING' in stdout else False

    def is_container_present(self):
        """Check if container is existing on node.

        :returns: True if container is present.
        :rtype: bool
        :raises RuntimeError: If failed to get info about a container.
        """
        cmd = 'lxc-info --no-humanize --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        return False if int(ret) else True

    def _lxc_wait(self, state):
        """Wait for a specific container state.

        :param state: Specify the container state(s) to wait for.
        :type state: str
        :raises RuntimeError: If failed to wait for state of a container.
        """
        cmd = 'lxc-wait --name {c.name} --state "{s}"'\
            .format(c=self.container, s=state)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to wait for state "{s}" of container '\
                               '{c.name}.'.format(s=state, c=self.container))

    def _lxc_cgroup(self, state_object, value=''):
        """Manage the control group associated with a container.

        :param state_object: Specify the state object name.
        :param value: Specify the value to assign to the state object. If empty,
        then action is GET, otherwise is action SET.
        :type state_object: str
        :type value: str
        :raises RuntimeError: If failed to get/set for state of a container.
        """
        cmd = 'lxc-cgroup --name {c.name} {s} {v}'\
            .format(c=self.container, s=state_object, v=value)

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgset --copy-from / lxc')
        if int(ret) != 0:
            raise RuntimeError('Failed to copy cgroup settings from root.')

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            if value:
                raise RuntimeError('Failed to set {s} of container {c.name}.'
                                   .format(s=state_object, c=self.container))
            else:
                raise RuntimeError('Failed to get {s} of container {c.name}.'
                                   .format(s=state_object, c=self.container))


class Docker(ContainerEngine):
    """Docker implementation."""

    def create(self, force_create=True):
        """Pull an image or a repository from a registry.

        :param force_create: Destroy a container if exists and create.
        :type force_create: bool
        :raises RuntimeError: If failed to pull a container.
        """
        if self.is_container_running():
            if force_create:
                self.destroy()
            else:
                return

        cmd = 'docker pull {c.image_spec}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
        if int(ret) != 0:
            raise RuntimeError('Failed to create container {c.name}.'
                               .format(c=self.container))

    def start(self):
        """Start container.

        :raises RuntimeError: If failed to start container.
        """
        env_var = '{0}'\
            .format(' '.join('--env %s' % var for var in self.container.env))

        cpuset_cpus = ','.join(str(cpu) for cpu in self.container.cpuset_cpus)

        cmd = 'docker run '\
            '--detach --interactive --tty --name {c.name} {e} '\
            '--cgroup-parent "" '\
            '--cpuset-mems={c.cpuset_mems} '\
            '--cpuset-cpus={p} '\
            '--volume {c.host_dir}:{c.guest_dir} '\
            '--privileged {c.image_spec}'.format(c=self.container,
                                                 e=env_var,
                                                 p=cpuset_cpus)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to start container {c.name}'
                               .format(c=self.container))

    def stop(self):
        """Stop running container.

        :raises RuntimeError: If failed to stop container.
        """
        cmd = 'docker stop {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to stop container {c.name}.'
                               .format(c=self.container))

    def destroy(self):
        """Remove a container.

        :raises RuntimeError: If failed to remove container.
        """
        cmd = 'docker rm --force {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to destroy container {c.name}.'
                               .format(c=self.container))

    def info(self):
        """Return low-level information on Docker objects.

        :raises RuntimeError: If failed to get info about a container.
        """
        cmd = 'docker inspect {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))

    def execute(self, command):
        """Start a process inside a running container. Runs the specified
        command inside the container specified by name. The container has to
        be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If failed to run the command in a container.
        """
        cmd = "docker exec --interactive {c.name} /bin/sh -c '{k}'"\
            .format(c=self.container, k=command)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError('Failed to run "{k}" inside container {c.name}.'
                               .format(k=command, c=self.container))

    def system_info(self):
        """Display the docker system-wide information.

        :raises RuntimeError: If failed to display information.
        """
        cmd = 'docker system info'

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get system info.')

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        """
        cmd = 'docker ps --all --quiet --filter name={c.name}'\
            .format(c=self.container)

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))
        return True if stdout else False

class Container(object):
    """Container object."""

    def __init__(self, node, name):
        # Container name
        self._name = name
        # DUT Node
        self._node = node
        # Host shared dir
        self._host_dir = '/tmp'
        # Guest shared dir
        self._guest_dir = Constants.CONTAINER_GUEST_DIR
        # Conatiner image specification
        self._image_spec = None
        # Container env variables
        self._env = ['LC_ALL="en_US.UTF-8"',
                     'DEBIAN_FRONTEND=noninteractive',
                     'ETCDV3_ENDPOINTS=172.17.0.1:2379']
        # Cpuset.Cpus
        self._cpuset_cpus = None
        # Cpuset.Mems
        self._cpuset_mems = None
        # Open SSH connetion
        self._ssh = SSH()
        self._ssh.connect(self._node)

    def __repr__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items())

    @property
    def name(self):
        """Getter.

        :returns: Container name.
        :rtype: str
        """
        return self._name

    @property
    def node(self):
        """Getter.

        :returns: DUT node.
        :rtype: dict
        """
        return self._node

    @property
    def host_dir(self):
        """Getter.

        :returns: Parent (host) dir.
        :rtype: str
        """
        return self._host_dir

    @host_dir.setter
    def host_dir(self, value):
        self._host_dir = value

    @property
    def guest_dir(self):
        """Getter.

        :returns: Container (guest) dir.
        :rtype: str
        """
        return self._guest_dir

    @guest_dir.setter
    def guest_dir(self, value):
        self._guest_dir = value

    @property
    def image_spec(self):
        """Getter.

        :returns: Container image specification.
        :rtype: str
        """
        return self._image_spec

    @image_spec.setter
    def image_spec(self, value):
        self._image_spec = value

    @property
    def env(self):
        """Getter.

        :returns: Container environment variables.
        :rtype: dict
        """
        return self._env

    @env.setter
    def env(self, value):
        self._env.append(value)

    @property
    def cpuset_cpus(self):
        """Getter.

        :returns: Container cpuset.cpus cgroup value.
        :rtype: str
        """
        return self._cpuset_cpus

    @cpuset_cpus.setter
    def cpuset_cpus(self, value):
        self._cpuset_cpus = value

    @property
    def cpuset_mems(self):
        """Getter.

        :returns: Container cpuset.mems cgroup value.
        :rtype: str
        """
        return self._cpuset_mems

    @cpuset_mems.setter
    def cpuset_mems(self, value):
        self._cpuset_mems = value

    @property
    def ssh(self):
        """Getter.

        :returns: SSH connection to node.
        :rtype: str
        """
        return self._ssh
