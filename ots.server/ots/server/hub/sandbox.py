# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
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

import sys
import uuid
import logging
import traceback

from ots.server.hub.options import Options
from ots.server.hub.options_factory import OptionsFactory

LOG = logging.getLogger(__name__)

DEBUG = False

class Sandbox(object):
    """
    The Essential Parameters for OTS to work.
    ... YA-Adaptation-L ...
  
    The Sandbox does it's best to provide this interface
    as quietly as possible. 

    Where possible when Exceptions are raised they are cached
    """

    #defaults if the worse comes to the worst...
    _IMAGE = "no_image"
    _EXAMPLE_SW_PRODUCT = "example_sw_product"
    _REQUEST_ID = "default_request_id"

    def __init__(self, sw_product, request_id, **kwargs):
        self._sw_product = sw_product
        self._request_id = request_id
        self._options = None
        self._kwargs = kwargs
        self._extended_options_dict = {}
        self._exc_info = None

    #########################
    # PROPERTIES
    #########################

    @property
    def sw_product(self):
        """
        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to
        """
        try:
            sw_product = str(self._sw_product).lower()
        except ValueError:
            LOG.error("SW Product cannot be cast to str using default")
            sw_product = self._EXAMPLE_SW_PRODUCT
        return sw_product

    @property
    def request_id(self):
        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client
        """
        try:
            request_id = str(self._request_id)
        except ValueError:
            LOG.error("Request ID cannot be cast to str using default")
            request_id = self._REQUEST_ID
        return request_id

    @property
    def testrun_uuid(self):
        """
        @type testrun_uuid: C{str}
        @param testrun_uuid: A globally unique identifier for the testrun
        """
        return uuid.uuid1().hex 

    @property
    def extended_options_dict(self):
        """
        @type extended_options_dict: C{dict}
        @param extended_options_dict: Additional options provided
        """
        return self._extended_options_dict

    @property
    def options(self):
        """
        @type options: L{Options}
        @param options: The Options for the Testrun
        """
        if self._options is None:
            try:
                LOG.debug("Initialising options with: '%s'"%(self._kwargs))
                options_factory = \
                    OptionsFactory(self.sw_product, self._kwargs)
                #Try to get these parameter out first 
                self._extended_options_dict = \
                    options_factory.extended_options_dict
                self._options = options_factory()
            except Exception, err:
                LOG.debug("Bootstrap Exception: %s"%(err))
                LOG.debug(traceback.format_exc())
                self._exc_info = sys.exc_info()
                self._options = Options(self._IMAGE)
                if DEBUG:
                    raise
        return self._options


    @property
    def is_hw_enabled(self):
        """
        @type is_hw_enabled: C{bool}
        @param is_hw_enabled: Is hw testing enabled?
        """        
        hw_packages = self.options.hw_packages
        if hasattr(hw_packages, "__iter__"):
            return bool(len(hw_packages))
        else:
            LOG.error("hw packages not iterable")
            return False

    @property 
    def is_host_enabled(self):
        """
        @type is_host_enabled: C{bool}
        @param is_host_enabled: Is host testing enabled
        """
        host_packages = self.options.host_packages
        if hasattr(host_packages, "__iter__"):
            return  bool(len(host_packages))
        else:
            LOG.error("host packages not iterable")
            return False

    ##############################
    # PUBLIC
    #############################

    def exc_info(self):
        """
        @type exc_info: C{tuple} type, value, traceback
        @param exc_info: The cached exc_info 
        """
        return self._exc_info
