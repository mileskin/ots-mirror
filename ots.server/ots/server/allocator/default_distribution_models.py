# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

"""
Default test package distribution models
"""

from ots.server.allocator.conductor_command import conductor_command

def perpackage_distribution(test_list, options):
    """Creates a separate task (conductor command) for each test package"""

    commands = []

    if not test_list:
        raise ValueError("test_list not defined for distribution model")

    if 'device' in test_list:
        for test_package in test_list['device'].split(","):
            options['test_packages'] = test_package
            cmd = conductor_command(options,
                                    host_testing = False,
                                    chroot_testing = False)
            commands.append(cmd)

    if 'host' in test_list:
        for test_package in test_list['host'].split(","):
            options['test_packages'] = test_package
            cmd = conductor_command(options,
                                    host_testing = True,
                                    chroot_testing = False)
            commands.append(cmd)

    if 'chroot' in test_list:
        for test_package in test_list['chroot'].split(","):
            options['test_packages'] = test_package
            cmd = conductor_command(options,
                                    host_testing = False,
                                    chroot_testing = True)

    return commands


def single_task_distribution(test_list, options):
    """Creates a single task (one command line) for all test packages"""

    single_cmd = []

    if not test_list:
        options['test_packages'] = ""
        cmd = conductor_command(options,
                                host_testing = False,
                                chroot_testing = False)
        single_cmd.extend(cmd)

    if 'device' in test_list:
        options['test_packages'] = test_list['device']
        cmd = conductor_command(options,
                                host_testing = False,
                                chroot_testing = False)
        single_cmd.extend(cmd)

    if 'host' in test_list:
        options['test_packages'] = test_list['host']
        cmd = conductor_command(options,
                                host_testing = True,
                                chroot_testing = False)
        # If there are device tests, have a ; to do them both.
        # Note: This means they're run under one timeout, in one shell.
        #       Coming improvements in task distribution could soon
        #       facilitate in improving this too.
        if single_cmd:
            single_cmd.append(';')
        single_cmd.extend(cmd)

    if 'chroot' in test_list:
        options['test_packages'] = test_list['chroot']
        cmd = conductor_command(options,
                                host_testing = False,
                                chroot_testing = True)

        if single_cmd:
            single_cmd.append(';')
        single_cmd.extend(cmd)

    return [single_cmd]

