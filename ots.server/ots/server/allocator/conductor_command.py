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
A module for generating conductor commands based on testrun options
"""

def conductor_command(options, host_testing, chroot_testing):
    """
    Creates a conductor command from the arguments.

    @type options: C{dict}
    @param options: String with test package names.
        Multiple packages must be separated by comma, without
        spaces. String may be empty.
        Packages are either for device or for host.

    @type host_testing: C{bool}
    @param host_testing: Whether options[test_packages]
        is assumed to contain tests for host. True or False.

    @rtype: C{list}
    @return: A list. First item is shell executable.
        The rest of the items are command line parameters.
    """
    cmd = ["conductor"]
    cmd.extend(["-u", options['image_url']])
    if options['emmc_flash_parameter']:
        cmd.extend(["-e", options['emmc_flash_parameter']])
    if options['testrun_id']:
        cmd.extend(["-i", str(options['testrun_id'])])
    if options['storage_address']:
        cmd.extend(["-c", options['storage_address']])
    if options['testfilter']:
        cmd.extend(["-f", options['testfilter']])
    if options['flasherurl']:
        cmd.extend(["--flasherurl", options['flasherurl']])
    if options['test_packages']:
        cmd.extend(["-t", options['test_packages']])
    # Use global timeout as conductor testrun timeout
    if options['timeout']:
        cmd.extend(["-m", str(options['timeout'])])
    if options['bootmode']:
        cmd.extend(["-b", options['bootmode']])
    if options['use_libssh2']:
        cmd.extend(["--libssh2"])
    if options.has_key('testplan_name'):
        cmd.extend(["-p", options['testplan_name']])

    if host_testing == True:
        cmd.extend(['-o'])

    if chroot_testing == True:
        cmd.extend(["--chrooted", "--rootstrapurl=%s" % options["rootstrap"]])

    return cmd
