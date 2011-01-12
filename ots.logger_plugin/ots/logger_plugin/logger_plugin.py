# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Ville Ilvonen <ville.p.ilvonen@nokia.com>
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

# Ignoring warnings because this is plugin
# pylint: disable=W0613
# pylint: disable=R0903

"""
The LoggerPlugin is a Publisher 

That adds LocalHttpHandler to log handlers.
"""

from ots.common.framework.publisher_plugin_base import PublisherPluginBase
import logging
import datetime
import os
from ots.logger_plugin.localhandler import LocalHttpHandler

LOG_DIR = "/var/log/ots/"  # TODO: Log directory to config file

class LoggerPlugin(PublisherPluginBase):
    """
    Logger Plugin is an OTS Publisher  

    Adds an LocalHttpHandler to root logger
    """
    def __init__(self, request_id, testrun_uuid, sw_product, image, **kwargs):
        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param testrun_uuid: The unique identifier for the testrun

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type image : C{str}
        @param image : The URL of the image        
        """

        self._httphandler = None
        self._filehandler = None
        self._initialize_logger(testrun_uuid, request_id)
    
    def __del__(self):
        self._remove_logger()
    #############################################
    # Logger initialization
    #############################################
    def _initialize_logger(self, testrun_uuid, request_id):
        """
        initializes the logger
        """
        logging.basicConfig() # This makes sure default formatters get loaded. Otherwise exc_info is not processed
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        # HTTP handler for end users
        self._httphandler = LocalHttpHandler(testrun_uuid)
        self._httphandler.setLevel(logging.INFO) # No debug msgs to end users
        root_logger.addHandler(self._httphandler)

        # File handler for maintainers/developers
        log_id_string = _generate_log_id_string(request_id, testrun_uuid)
        format = '%(asctime)s  %(module)-12s %(levelname)-8s %(message)s'
        os.system("mkdir -p %s" % LOG_DIR)
        self._filehandler = logging.FileHandler(LOG_DIR+log_id_string)
        self._filehandler.setLevel(logging.DEBUG) # All messages to the files
        self._filehandler.setFormatter(logging.Formatter(format))
        root_logger.addHandler(self._filehandler)
        
    #############################################
    # Logger removal
    #############################################
    def _remove_logger(self):
        """
        removes the logger
        """
        if self._httphandler is not None:
            root_logger = logging.getLogger('')
            root_logger.removeHandler(self._httphandler)
            


def _generate_log_id_string(build_id, testrun_id):
    """
    Generates the log file name
    """
    request_id = "testrun_%s_request_%s_"% (testrun_id, build_id)
    request_id += str(datetime.datetime.now()).\
        replace(' ','_').replace(':','_').replace('.','_')
    return request_id
