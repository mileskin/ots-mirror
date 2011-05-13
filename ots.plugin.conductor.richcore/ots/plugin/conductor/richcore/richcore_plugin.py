# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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
OTS conductor plugin for rich-core processing.

NOTE: Requires ssh access to the build and core processing servers with
key-based authentication.
"""
import os
import logging
import configobj
import subprocess

from ots.common.framework.api import ConductorPluginBase
from ots.worker.command import Command
from ots.worker.command import SoftTimeoutException
from ots.worker.command import HardTimeoutException
from ots.worker.command import CommandFailed
from ots.worker.conductor.conductor_config \
        import TIMEOUT_FETCH_ENVIRONMENT_DETAILS, HW_COMMAND

DEFAULT_CONFIG_FILE = "/etc/ots_plugin_conductor_richcore.conf"
RICH_CORE_FILE_SUFFIX = ".rcore.lzo"
COPY_RICHCORE_TO_PROCESSING_QUEUE = "ssh %s@%s mkdir %s; scp %s %s@%s:%s"
COPY_LOCAL_FILE_TO_REMOTE = "scp %s %s@%s:%s"
DEBUG_PACKAGE_LIST_FILE_NAME = "%s_debug_package_list"
GET_BUILD_ID_COMMAND = "grep \"BUILD\" /etc/meego-release | cut -d\  -f 2"
LOG = logging.getLogger(__name__)

class RichCorePlugin(ConductorPluginBase):
    """
    OTS conductor plugin for rich-core processing.
    """

    def __init__(self, options):

        self.process_rich_core_dumps = options.save_rich_core_dumps
        self.result_dir = ""
        self.target = None
        self.target_ip_address = options.target_ip_address 
        
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            self.process_rich_core_dumps = False
            raise Exception("%s not found" % (DEFAULT_CONFIG_FILE))

        LOG.info("Plugin: ots.plugin.conductor.richcore loaded.")

    def before_testrun(self):
        """
        Called before testrun. Fetches debug package list from the device and
        copies it to the build server.
        """

        if self.process_rich_core_dumps == False:
            return

        config = configobj.ConfigObj(DEFAULT_CONFIG_FILE).get("debug_build")
        host = config.get("host")

        user = config.get("user")
        if user == "":
            user = os.getenv("USER")

        # Enable debug repos        
        LOG.debug("Enabling debug repos in Device Under Test...")
        cmdstr = self.target.get_command_to_enable_debug_repos()
        self._execute_ssh_command(cmdstr)

        # Get build id
        cmdstr = HW_COMMAND % (self.target_ip_address, GET_BUILD_ID_COMMAND)
        LOG.debug("Getting BUILD ID from Device Under Test...")
        cmd = self._execute_ssh_command(cmdstr)
        build_id = cmd.stdout.strip()

        if cmd.return_value != 0 or build_id == "":
            LOG.warning("Failed to get BUILD ID. Giving up..." )
            self.process_rich_core_dumps = False
            return
        else:
            LOG.debug("Got BUILD ID: %s" % build_id)

        filename = DEBUG_PACKAGE_LIST_FILE_NAME % build_id
        path = os.path.join(self.result_dir, filename)

        # Search for debug packages
        LOG.debug("Search debug debug packages for image...")
        cmdstr = self.target.get_command_to_list_debug_packages()
        cmd = self._execute_ssh_command(cmdstr)

        if cmd.stdout == "":
            LOG.warning("No debug packages found. Giving up..." )
            self.process_rich_core_dumps = False
            return

        # Save list locally and copy to remote processing machine 
        try:
            list_file = open(path, "w")
            list_file.write(cmd.stdout)
            list_file.close()
        except IOError:
            LOG.warning("IOError when creating list_file %s." % path)
            self.process_rich_core_dumps = False
            return
        else:
            LOG.debug("Created new list_file: %s" % path)

        cmdstr = COPY_LOCAL_FILE_TO_REMOTE % \
                (path, user, host,
                 os.path.join(config.get("dbg_list_path"), filename))

        LOG.debug("Executing:  %s ..." % cmdstr)
        if subprocess.call(cmdstr, shell=True):
            LOG.warning("Failed to execute: %s ..." % cmdstr)

    def after_testrun(self):
        """
        Called after testrun. Uploads rich-core dumps to the analysis
        back-end server.
        """

        if self.result_dir != "" and self.process_rich_core_dumps == True:
            files = os.listdir(self.result_dir)

            config = configobj \
                .ConfigObj(DEFAULT_CONFIG_FILE).get("core_processing")
            host = config.get("host")
                
            user = config.get("user")
            if user == "":
                user = os.getenv("USER")

            for _file in files:
                results_path = os.path.join(self.result_dir, _file, "results")
                
                if os.path.isdir(results_path):
                    LOG.debug("Locating rich-core dumps from:  %s ..." \
                              % results_path)
                    result_files = os.listdir(results_path)

                    for result_file in result_files: 
                        if result_file.endswith(RICH_CORE_FILE_SUFFIX):
                            local_rcore_path = os.path.join(results_path,
                                                            result_file)
                            remote_rcore_path = \
                                os.path.join(config.get("core_queue_path"),
                                             result_file.split( \
                                                    RICH_CORE_FILE_SUFFIX)[0])

                            remote_copy_cmd = \
                                COPY_RICHCORE_TO_PROCESSING_QUEUE % \
                                (user, host, remote_rcore_path,
                                 local_rcore_path, user, host,
                                 os.path.join(remote_rcore_path, "core"))

                            LOG.debug("Executing:  %s ..." % remote_copy_cmd)

                            if subprocess.call(remote_copy_cmd, shell=True):
                                LOG.warning("Failed to execute: %s, "
                                            "keep going..." % remote_copy_cmd)
                                                    
                            try:
                                os.remove(local_rcore_path)
                            except OSError:
                                LOG.warning("Failed to remove %s, keep "
                                            "going..." % local_rcore_path)

    def set_target(self, hw_target):
        """
        Set hardware target

        @type hw_target: C{ots.worker.conductor.testtarget.TestTarget}
        @param hw_target: Hardware specific communication class
        """

        self.target = hw_target
                
    def set_result_dir(self, result_dir):
        """
        Sets result file directory

        @type result_dir: C{string}
        @param result_dir: Result file directory path
        """

        self.result_dir = result_dir

    def _execute_ssh_command(self, cmdstr):
        """
        Executes a command in the hardware using ssh

        @type command: C{string}
        @param command: Command string to execute
        @return ots.worker.command
        """
        cmd = Command(cmdstr, soft_timeout = TIMEOUT_FETCH_ENVIRONMENT_DETAILS,
                      hard_timeout = TIMEOUT_FETCH_ENVIRONMENT_DETAILS + 5)

        try:
            cmd.execute()
        except (SoftTimeoutException, HardTimeoutException):
            LOG.warning("Failed to execute ssh command. (command %s " \
                        "timed out)" % (cmdstr))
        except CommandFailed:
            # Print debug on command failure. It still might be ok.
            LOG.debug("Failed to execute ssh command. (command %s " \
                        "returned %s)" % (cmdstr, \
                        cmd.return_value))
        else:
            LOG.debug("Command executed successfully!")
        
        return cmd
