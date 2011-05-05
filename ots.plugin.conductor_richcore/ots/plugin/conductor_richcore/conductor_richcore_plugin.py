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
OTS 0.8.4 compatible conductor plugin for rich-core processing

NOTE: Requires ssh access to the back-end server with key-based authentication
"""
import os
import logging
import configobj
import subprocess
from ots.common.framework.api import ConductorPluginBase

RICH_CORE_FILE_SUFFIX = ".rcore.lzo"
COPY_COMMAND_LOCAL_FILE_TO_REMOTE = "ssh %s@%s mkdir %s; scp %s %s@%s:%s"
LOG = logging.getLogger(__name__)
DEFAULT_CONFIG_FILE = "/etc/ots_plugin_conductor_richcore.conf"

class RichCorePlugin(ConductorPluginBase):
    """
    OTS 0.8.4 compatible conductor plugin for rich-core processing
    """

    def __init__(self, options):

        self.process_rich_core_dumps = options.save_rich_core_dumps
        self.result_dir = ""
        
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            raise Exception("%s not found" % (DEFAULT_CONFIG_FILE))

        self.config = configobj.ConfigObj(DEFAULT_CONFIG_FILE).get("ots.plugin.conductor.richcore")

        LOG.info("Plugin: ots.plugin.conductor_richcore loaded.")

    def before_testrun(self):
        """
        Called before testrun.
        """        
        
    def after_testrun(self):
        """
        Called after testrun. Uploads rich-core dumps to the analysis back-end server
        """

        if self.result_dir != "" and self.process_rich_core_dumps == True:
            files = os.listdir(self.result_dir)
                
            user = self.config.get('user')
            if user == "":
                user = os.getenv("USER")

            host = self.config.get('host')

            for file in files:
                results_path = os.path.join(self.result_dir, file, "results")
                
                if os.path.isdir(results_path):
                    LOG.debug("Locating rich-core dumps from:  %s ..." % results_path)
                    result_files = os.listdir(results_path)

                    for result_file in result_files: 
                        if result_file.endswith(RICH_CORE_FILE_SUFFIX):
                            local_rcore_path = os.path.join(results_path, result_file)
                            remote_rcore_path = os.path.join(self.config.get('path'),
                                result_file.split(RICH_CORE_FILE_SUFFIX)[0])
                                      
                            remote_copy_cmd = COPY_COMMAND_LOCAL_FILE_TO_REMOTE % \
                                (user, host, remote_rcore_path, local_rcore_path, 
                                user, host, os.path.join(remote_rcore_path, "core"))

                            LOG.debug("Executing:  %s ..." % remote_copy_cmd)

                            if subprocess.call(remote_copy_cmd, shell=True):
                                LOG.warning("Failed to execute: %s, keep going..." \
                                    % remote_copy_cmd)

                            remove_file_str = "rm -f %s" % local_rcore_path
                            LOG.debug("Executing:  %s ..." % remove_file_str)

                            if subprocess.call(remove_file_str, shell=True):
                                LOG.warning("Failed to execute: %s, keep going..." \
                                    % remove_file_str)
                
    def set_result_dir(self, result_dir):
        """
        Sets result file directory

        @type result_dir: C{string}
        @param result_dir: Result file directory path
        """

        self.result_dir = result_dir
