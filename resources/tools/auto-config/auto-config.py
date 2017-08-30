#!/usr/bin/python

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

"""Auto Configuration Main Entry"""

import re
import os
import sys

from resources.libraries.python.AutoConfig import AutoConfig
from resources.libraries.python.ssh import SSH

VPP_DEFAULT_CONFIGURATION_FILE = './configs/auto-config.yaml'
VPP_SYSTEM_CONFIGURATION_FILE = './configs/system-config.yaml'
VPP_HUGE_PAGE_FILE = '/etc/sysctl.d/80-vpp.conf'
VPP_STARTUP_FILE = '/etc/vpp/startup.conf'
VPP_GRUB_FILE = '/etc/default/grub'


def autoconfig_yn(question, default):
    """
    Ask the user a yes or no question.

    :param question: The text of the question
    :param default: Value to be returned if '\n' is entered
    :type question: string
    :type default: string
    :returns: The Answer
    :rtype: string
    """
    input_valid = False
    default = default.lower()
    answer = ''
    while not input_valid:
        answer = raw_input(question)
        if len(answer) == 0:
            answer = default
        if re.findall(r'[YyNn]', answer):
            input_valid = True
            answer = answer[0].lower()
        else:
            print "Please answer Y, N or Return."

    return answer


def autoconfig_cp(node, ssh, src, dst):
    """
    Copies a file, saving the original if needed.

    :param node: Node dictionary with cpuinfo.
    :param ssh: ssh class
    :param src: Source File
    :param dst: Destination file
    :type node: dict
    :type ssh: class
    :type src: string
    :type dst: string
    :raises RuntimeError: If command fails
    """

    # If the destination file exist, create a copy if one does not already
    # exist
    ofile = dst + '.orig'
    (ret, stdout, stderr) = ssh.exec_command('ls {}'.format(dst))
    if ret == 0:
        cmd = 'cp {} {}'.format(dst, ofile)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.
                               format(cmd,
                                      node['host'],
                                      stdout,
                                      stderr))

    # Copy the source file
    cmd = 'cp {} {}'.format(src, dst)
    (ret, stdout, stderr) = ssh.exec_command(cmd)
    if ret != 0:
        raise RuntimeError('{} failed on node {} {}'.
                           format(cmd, node['host'], stderr))


def autoconfig_diff(node, ssh, src, dst):
    """
    Returns the diffs of 2 files.

    :param node: Node dictionary with cpuinfo.
    :param ssh: ssh class
    :param src: Source File
    :param dst: Destination file
    :type node: dict
    :type ssh: class
    :type src: string
    :type dst: string
    :returns: The Answer
    :rtype: string
    :raises RuntimeError: If command fails
    """

    # Diff the files and return the output
    cmd = "diff {} {}".format(src, dst)
    (ret, stdout, stderr) = ssh.exec_command(cmd)
    if stderr != '':
        raise RuntimeError('{} failed on node {} {} {}'.
                           format(cmd,
                                  node['host'],
                                  ret,
                                  stderr))

    return stdout


def autoconfig_show_system():
    """
    Shows the system information.

    """

    acfg = AutoConfig(VPP_DEFAULT_CONFIGURATION_FILE)

    acfg.discover()

    acfg.sys_info()


def autoconfig_hugepage_apply(node, ssh):
    """
    Apply the huge page configuration.
    :param node: The node structure
    :param ssh: The ssh class
    :type node: dict
    :type: ssh: class
    :returns: -1 if the caller should return, 0 if not
    :rtype: int

    """

    dfile = './dryrun' + VPP_HUGE_PAGE_FILE
    diffs = autoconfig_diff(node, ssh, VPP_HUGE_PAGE_FILE, dfile)
    if diffs != '':
        print "These are the changes we will apply to"
        print "the huge page file ({}).\n".format(VPP_HUGE_PAGE_FILE)
        print diffs
        answer = autoconfig_yn(
            "\nAre you sure you want to apply these changes [y/N]? ",
            'n')
        if answer == 'n':
            return -1

        # Copy and sysctl
        autoconfig_cp(node, ssh, dfile, VPP_HUGE_PAGE_FILE)
        cmd = "sysctl -p {}".format(VPP_HUGE_PAGE_FILE)
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.
                               format(cmd, node['host'], stdout, stderr))
    else:
        print '\nThere are no changes to the huge page configuration.'

    return 0


def autoconfig_vpp_apply(node, ssh):
    """
    Apply the vpp configuration.

    :param node: The node structure
    :param ssh: The ssh class
    :type node: dict
    :type: ssh: class
    :returns: -1 if the caller should return, 0 if not
    :rtype: int

    """

    cmd = "service vpp stop"
    (ret, stdout, stderr) = ssh.exec_command(cmd)
    if ret != 0:
        raise RuntimeError('{} failed on node {} {} {}'.
                           format(cmd, node['host'], stdout, stderr))

    dfile = './dryrun' + VPP_STARTUP_FILE
    diffs = autoconfig_diff(node, ssh, VPP_STARTUP_FILE, dfile)
    if diffs != '':
        print "These are the changes we will apply to"
        print "the VPP startup file ({}).\n".format(VPP_STARTUP_FILE)
        print diffs
        answer = autoconfig_yn(
            "\nAre you sure you want to apply these changes [y/N]? ",
            'n')
        if answer == 'n':
            return -1

        # Copy the VPP startup
        autoconfig_cp(node, ssh, dfile, VPP_STARTUP_FILE)
    else:
        print '\nThere are no changes to VPP startup.'

    return 0


def autoconfig_grub_apply(node, ssh):
    """
    Apply the grub configuration.

    :param node: The node structure
    :param ssh: The ssh class
    :type node: dict
    :type: ssh: class
    :returns: -1 if the caller should return, 0 if not
    :rtype: int

    """
    print "\nThe configured grub cmdline looks like this:"
    configured_cmdline = node['grub']['default_cmdline']
    current_cmdline = node['grub']['current_cmdline']
    print configured_cmdline
    print "\nThe current boot cmdline looks like this:"
    print current_cmdline
    question = "\nDo you want to keep the current boot cmdline [Y/n]? "
    answer = autoconfig_yn(question, 'y')
    if answer == 'n':
        node['grub']['keep_cmdline'] = False

        # Diff the file
        dfile = './dryrun' + VPP_GRUB_FILE
        diffs = autoconfig_diff(node, ssh, VPP_GRUB_FILE, dfile)
        if diffs != '':
            print "These are the changes we will apply to"
            print "the GRUB file ({}).\n".format(VPP_GRUB_FILE)
            print diffs
            answer = autoconfig_yn(
                "\nAre you sure you want to apply these changes [y/N]? ",
                'n')
            if answer == 'n':
                return -1

            # Copy and update grub
            autoconfig_cp(node, ssh, dfile, VPP_GRUB_FILE)
            cmd = "update-grub"
            (ret, stdout, stderr) = ssh.exec_command(cmd)
            if ret != 0:
                raise RuntimeError('{} failed on node {} {} {}'.
                                   format(cmd,
                                          node['host'],
                                          stdout,
                                          stderr))
            print "There have been changes to the GRUB config a",
            print "reboot will be required."
            return -1
        else:
            print '\nThere are no changes to the GRUB config.'

    return 0


def autoconfig_apply():
    """
    Apply the configuration.

    Show the diff of the dryrun file and the actual configuration file
    Copy the files from the dryrun directory to the actual file.
    Peform the system function

    """

    acfg = AutoConfig(VPP_SYSTEM_CONFIGURATION_FILE)

    print "\nWe are now going to configure your system(s).\n"
    answer = autoconfig_yn("Are you sure you want to do this [y/N]? ", 'n')
    if answer == 'n':
        return

    nodes = acfg.get_nodes()
    for i in nodes.items():
        node = i[1]

        ssh = SSH()
        ssh.connect(node)

        # Huge Pages
        ret = autoconfig_hugepage_apply(node, ssh)
        if ret != 0:
            return

        # VPP
        ret = autoconfig_vpp_apply(node, ssh)
        if ret != 0:
            return

        # Grub
        ret = autoconfig_grub_apply(node, ssh)
        if ret != 0:
            return

        # Everything is configured start vpp
        cmd = "service vpp start"
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {} {}'.
                               format(cmd, node['host'], stdout, stderr))


def autoconfig_dryrun():
    """
    Execute the dryrun function.

    """
    acfg = AutoConfig(VPP_DEFAULT_CONFIGURATION_FILE)

    # Discover
    acfg.discover()

    # Modify the devices
    acfg.modify_devices()

    # Modify CPU
    acfg.modify_cpu()

    # Calculate the cpu parameters
    acfg.calculate_cpu_parameters()

    # Apply the startup
    acfg.apply_vpp_startup()

    # Apply the grub configuration
    acfg.apply_grub_cmdline()

    # Huge Pages
    acfg.modify_huge_pages()
    acfg.apply_huge_pages()


def autoconfig_not_implemented():
    """
    This feature is not implemented

    """
    print "This Feature is not implented yet"


def autoconfig_main_menu():
    """
    The auto configuration main menu

    """

    main_menu_text = '\nWhat would you like to do?\n\n\
1) Show basic system information\n\
2) Dry Run (Will save the configuration files in ./dryrun for inspection)\n\
       and user input in ./config/auto-config.yaml\n\
3) Full configuration (WARNING: This will change the system configuration)\n\
4) Dry Run from ./auto-config.yaml (will not ask questions).\n\
5) Install/Uninstall VPP.\n\
6) Install QEMU patch (Needed when running openstack).\n\
9 or q) Quit'

    print "{}".format(main_menu_text)

    input_valid = False
    answer = ''
    while not input_valid:
        answer = raw_input("\nCommand: ")
        if len(answer) > 1:
            print "Please enter only 1 character."
            continue
        if re.findall(r'[Qq1-79]', answer):
            input_valid = True
            answer = answer[0].lower()
        else:
            print "Please enter a character between 1 and 7 or 9."

    if answer == '9':
        answer = 'q'
    return answer


def autoconfig_main():
    """
    The auto configuration main entry point

    """

    answer = ''
    while answer != 'q':
        answer = autoconfig_main_menu()
        if answer == '1':
            autoconfig_show_system()
        elif answer == '2':
            autoconfig_dryrun()
        elif answer == '3':
            autoconfig_apply()
        elif answer == '9' or answer == 'q':
            return
        else:
            autoconfig_not_implemented()


def autoconfig_setup():
    """
    The auto configuration setup function.

    We will copy the configuration files to the dryrun directory.

    """

    acfg = AutoConfig(VPP_DEFAULT_CONFIGURATION_FILE)

    print "\nWelcome to the FDIO system configuration utility"

    print "\nWe'll create or modify these files:"
    print "    /etc/vpp/startup.conf"
    print "    /etc/sysctl.d/80-vpp.conf"
    print "    /etc/default/grub"

    print "\nBefore we change them, we'll create working copies in ./dryrun"
    print "Please inspect them carefully before proceeding!"

    print "\nIf you are running this utility for the first time, \
please answer y."
    answer = autoconfig_yn(
        "Do you want to copy the current system files to ./dryrun [y/N]? ", 'n')
    if answer == 'y':

        nodes = acfg.get_nodes()
        for i in nodes.items():
            node = i[1]

            ssh = SSH()
            ssh.connect(node)

            filename = '/etc/vpp/startup.conf'
            autoconfig_cp(node, ssh, filename, './dryrun{}'.format(filename))
            filename = '/etc/sysctl.d/80-vpp.conf'
            autoconfig_cp(node, ssh, filename, './dryrun{}'.format(filename))
            filename = '/etc/default/grub'
            autoconfig_cp(node, ssh, filename, './dryrun{}'.format(filename))


if __name__ == '__main__':

    # Check for root
    if not os.geteuid() == 0:
        sys.exit('\nPlease run the FDIO Configuration Utility as root.')

    # Set the PYTHONPATH
    sys.path.append('../../..')

    # Setup
    autoconfig_setup()

    # Main menu
    autoconfig_main()
