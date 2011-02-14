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
# pylint: disable-msg=W0613
# pylint: disable-msg=R0903

"""
The Monitor Plugin for OTS
"""

import logging

from ots.common.framework.api import PublisherPluginBase
from ots.server.distributor.api import DTO_SIGNAL
from ots.common.dto.api import Monitor

LOG = logging.getLogger(__name__)


class MonitorPlugin(PublisherPluginBase):
    """
    Monitor Plugin  
    """
    def __init__(self):
        """
        initialization
        """
        DTO_SIGNAL.connect(self._callback)
        LOG.info('Monitor Plugin loaded')

    def set_monitors(self, monitors):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        LOG.info("got monitors")

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
        LOG.info("Got signal!")
        LOG.info(dto)
        LOG.info(signal)
        if isinstance(dto, Monitor):
            LOG.info(dto.duration)
