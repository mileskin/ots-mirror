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
import time
import datetime

from ots.common.framework.api import PublisherPluginBase
from ots.common.dto.monitor import Monitor, MonitorType
from ots.plugin.history.models import Package, History
LOG = logging.getLogger(__name__)


class HistoryPlugin(PublisherPluginBase):
    """
    Distribution history plug-in  
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
        LOG.info('Distribution history plug-in loaded')
        
        self._testrun_id = testrun_uuid
        self._request_id = request_id
        self._test_packages = dict()
        
    def set_tested_packages(self, packages):
        """
        @type packages : C{ots.common.dto.packages}
        @param packages: The Test Packages that were run
        """
        for (env, pkg_list) in packages.items():
            for tested_package in pkg_list:
                if not self._test_packages.has_key(tested_package):
                    LOG.warning("%s package has no duration!" % tested_package)
    
    def set_monitors(self, monitors):
        """
        @type monitors: C{ots.common.dto.monitor}
        @param monitors: Monitor class
        """
        
        if monitors.type == MonitorType.TEST_PACKAGE_STARTED:
            test_package = monitors.description
            start_time = time.time()
            
            self._test_packages[test_package] = (start_time, None)
            LOG.debug("Test package started %s : %d" % (test_package, start_time))
            
        elif monitors.type == MonitorType.TEST_PACKAGE_ENDED:
            test_package = monitors.description
            end_time = time.time()
            if self._test_packages.has_key(test_package):
                (start_time, duration) = self._test_packages.get(test_package)
                duration = end_time - start_time
                self._test_packages[test_package] = (start_time, duration)
                LOG.debug("Test package ended %s : %d" % (test_package, end_time))
            else:
                LOG.warning("Test package (%s) ended without starting?!" % 
                            test_package)
    
    def publish(self):
        """
        Publish the results of the Testrun
        """
        try:
            for (test_package, data) in self._test_packages.items():
                
                start_time = datetime.datetime.fromtimestamp(data[0])
                duration = data[1]
                
                if duration is None:
                    continue
                
                db_package = Package.objects.filter(package_name = test_package)
                
                if db_package.count() == 0:
                    db_package = Package(package_name = test_package)
                    db_package.save()
                else:
                    db_package = db_package[0]
                
                history = History(package_id = db_package,
                                  start_time = start_time,
                                  duration = duration,
                                  testrun_id = self._testrun_id,
                                  verdict = 0)
                history.save()
            
            LOG.info("history data saved")                    
                
        except (TypeError, AttributeError, IntegrityError), error:
            LOG.error("History object creation failed: %s" % error)
