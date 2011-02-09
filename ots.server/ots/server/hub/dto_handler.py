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
Handler for the DTOs

Collects DTOs by connecting to the DTO_SIGNAL 
"""

import logging

from logging import LogRecord

from ots.common.dto.api import Packages, Results, Environment, Monitor
from ots.server.distributor.api import DTO_SIGNAL

LOG = logging.getLogger(__name__)

class DTOHandler(object):
    """
    Collects:

     - results_xmls
     - tested_packages
     - expected_packages#
     - monitors
     - exceptions

    OTS_Exceptions are re-raised
    LogRecords are logged
    """


    def __init__(self):
        self.results = []
        self.tested_packages = {}
        self.expected_packages = {}
        self.monitors = []
        self.exceptions = []
        DTO_SIGNAL.connect(self._callback)

    ###########################################
    # DTO HANDLERS
    ###########################################
    
    def _results(self, result):
        """
        @type result: L{ots.common.api.ResultObject}
        @param result: The Results Objects

        Handler for Results
        """
        environment = result.environment
        LOG.debug("Received result file for %s"%(environment))
        packages = Packages(environment, [result.package])
        if result.is_result_xml:
            if not self.tested_packages:
                self.tested_packages = packages
            else:
                self.tested_packages.update(packages)
        self.results.append(result)

    def _packages(self, packages): 
        """
        @type packages: L{ots.common.dto.environment.packages}
        @param packages: The Packages

        Handler for Packages
        """
        LOG.debug("Received packages: %s" % (packages))
        if not self.expected_packages:
            self.expected_packages = packages
        else:
            self.expected_packages.update(packages)

    ##################################
    # CALLBACK
    ##################################

    def _callback(self, signal, dto, **kwargs):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type dto: L{ots.common.dto}
        @param dto: An OTS Data Transfer Object

        The callback for DTO_SIGNAL 
        Multimethod that delegates
        data to the handler depending on <type>
        """
        if isinstance(dto, Exception):
            logger = logging.getLogger(__name__)
            logger.error(dto)
            self.exceptions.append(dto)
        elif isinstance(dto, LogRecord):
            logger = logging.getLogger(dto.name)
            logger.log(dto.levelno, dto.msg)
        elif isinstance(dto, Results):
            self._results(dto)
        elif isinstance(dto, Packages):
            self._packages(dto)
        elif isinstance(dto, Monitor):
            self.monitors.append(dto)
        else:
            LOG.debug("Unknown DTO: '%s'"%(dto))
