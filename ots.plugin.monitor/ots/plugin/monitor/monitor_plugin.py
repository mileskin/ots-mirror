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

from ots.common.dto.monitor import Monitor
from ots.common.framework.api import PublisherPluginBase
from ots.django.monitor.models import Testrun, Event, Package


LOG = logging.getLogger(__name__)


class MonitorPlugin(PublisherPluginBase):
    """
    Monitor Plugin  
    """
    def __init__(self, request_id, testrun_uuid, sw_product, image, **kwargs):
        """
        Initialization
        
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param testrun_uuid: The unique identifier for the testrun

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type image : C{str}
        @param image : The URL of the image
        """
        LOG.info('Monitor Plugin loaded')

        try:
            # Create a new testrun object to db
            # TODO: check parameter fillings
            self._testrun = Testrun(testrun_id=testrun_uuid,
                                    device_group='',
                                    queue='',
                                    configuration='',
                                    host_worker_instances='',
                                    requestor='',
                                    request_id=request_id)
            self._testrun.save()
        except (TypeError, AttributeError), error:
            LOG.error("Testrun object creation failed: %s" % error)

    def set_monitors(self, monitors):
        """
        @type monitors: C{ots.common.dto.monitor}
        @param monitors: Monitor class
        """
        LOG.debug("Got monitor information: %s" % monitors)
        
        try:
            event = Event(testrun_id=self._testrun.testrun_id,
                          event_name=monitors.type,
                          event_emit=monitors.emitted,
                          event_receive=monitors.received)
            self._testrun.add(event)
        except (TypeError, AttributeError), error:
            LOG.error("Event object creation failed: %s" % error)
