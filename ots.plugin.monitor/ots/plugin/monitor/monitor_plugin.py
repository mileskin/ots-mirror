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

from ots.common.dto.monitor import Monitor, MonitorType
from ots.common.framework.api import PublisherPluginBase
from ots.plugin.monitor.models import Testrun, Event


LOG = logging.getLogger(__name__)


class MonitorPlugin(PublisherPluginBase):
    """
    Monitor Plugin  
    """
    def __init__(self, request_id, testrun_uuid, sw_product, image,
                 notify_list = None,
                 device = None,
                 **kwargs):
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
        
        @type notify_list : C{list}
        @param notify_list : Request email list, first one is the requestor
        
        @type device : C{dict}
        @param device : Device options as dictionary
        
        """
        LOG.info('Monitor Plugin loaded')

        self._testrun_result = ''
        requestor = ''
        device_group = ''

        if notify_list and len(notify_list) > 0:
            requestor = notify_list[0]

        if device:
            if not isinstance(device, str):
                device_group = device.get('devicegroup', "invalid")
        
        if device_group == '':
            LOG.warning("Empty devicegroup defined!")
            device_group = "invalid"

        try:
            # Create a new testrun object to DB
            # TODO: check which queue should be used in queue parameter
            self._testrun = Testrun(testrun_id=testrun_uuid,
                                    device_group=device_group,
                                    queue="",
                                    configuration=kwargs.__str__(),
                                    host_worker_instances='',
                                    requestor=requestor,
                                    request_id=request_id)
            self._testrun.save()
        except (TypeError, AttributeError), error:
            LOG.error("Testrun object creation failed: %s" % error)

    def add_monitor_event(self, monitors):
        """
        Monitor information catch
        Event information parameters hide different information depending of
        MonitorType, for more info see MonitorType class comments.
        
        @type monitors: C{ots.common.dto.monitor}
        @param monitors: Monitor class
        """
        LOG.debug("Got monitor information: %s" % monitors)
        
        try:
            event = Event(testrun_id=self._testrun,
                          event_name=monitors.type,
                          event_emit=monitors.emitted,
                          event_receive=monitors.received)
            event.save()
        except (TypeError, AttributeError), error:
            LOG.error("Event object creation failed: %s" % error)

        try:
            LOG.debug("Monitor type: %s" % monitors.type)
            if monitors.type == MonitorType.TASK_INQUEUE:
                self._update_testrun_state('0')
            elif monitors.type == MonitorType.TASK_ONGOING:
                self._update_host_worker_instances(monitors.sender)
                self._update_testrun_state('1')
            elif monitors.type == MonitorType.TASK_ENDED:
                self._update_host_worker_instances(monitors.sender)
        except (TypeError, AttributeError), error:
            LOG.error("Testrun object update failed: %s" % error)

    def set_testrun_result(self, testrun_result):
        """
        Set testrun result according to parameter value
        
        @type testrun_result: C{str}
        @param testrun_result: The testrun result
        """
        self._testrun_result = {
                                'PASS'  : '2',
                                'FAIL'  : '3',
                                'ERROR' : '4',
                                }[testrun_result]

    def publish(self):
        """
        Make sure that testrun state is set
        """
        self._update_testrun_state()

    def set_exception(self, exception):
        """
        Set error value to DB
        
        @type: C{Exception}
        @param: The Exception raised by the Testrun 
        """
        self._testrun.error = exception
        self._testrun.save()

    ###########################################
    # Helpers
    ###########################################

    def _update_testrun_state(self, state=None):
        """
        Update testrun state.
        
        @type state : C{str}
        @param state: The result of the Testrun
        """
        if state:
            self._testrun.state = state
        else:
            self._testrun.state = self._testrun_result

        self._testrun.save()

    def _update_host_worker_instances(self, host_name):
        """
        Add worker instance to DB
        
        @type host_name: C{str}
        @param host_name: Host name of worker machine
        """
        if self._testrun.host_worker_instances.find(host_name) < 0:
            if len(host_name) == 0:
                self._testrun.host_worker_instances = str(host_name)
            else:
                self._testrun.host_worker_instances += ' ' + str(host_name)

            self._testrun.save()
