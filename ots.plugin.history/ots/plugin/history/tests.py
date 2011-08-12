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

import unittest
import logging
import uuid
import time
import random

from ots.plugin.history.models import Package, History
from ots.plugin.history.history_plugin import HistoryPlugin
from ots.plugin.history.distribution_model import get_test_package_history, history_model, get_model
from ots.plugin.history.schedule_algo import group_packages
from ots.common.dto.monitor import Monitor, MonitorType

NUM_OF_TESTPACKAGES = 5

def _create_test_data():

    for i in xrange(NUM_OF_TESTPACKAGES):
        
        db_pack = Package(package_name = "test-package" + str(i) + "-tests")
        db_pack.save()
            
        history = History(package_id = db_pack,
                          duration = i * 60 * 60,
                          testrun_id = uuid.uuid4().hex,
                          verdict = random.randint(0,4))
        history.save()


class TestHistoryPublisherPlugin(unittest.TestCase):
    """
    Unit tests for history publisher plugin
    """

    def setUp(self):
        """
        Unit test setup
        """

        _create_test_data()

    def tearDown(self):
        """
        Unit test tear down
        """
        # Deleting all data
        Package.objects.all().delete()
        History.objects.all().delete()
    
    def testCreateNew(self):
        plugin = HistoryPlugin("0001", "0001", "example_product", "no image")
        
        event_package1 = Monitor(event_type = MonitorType.TEST_PACKAGE_STARTED,
                                 sender = "ots-worker1",
                                 description = "test-newpackage-tests")
        plugin.add_monitor_event(event_package1)
        time.sleep(1)
        event_package1 = Monitor(event_type = MonitorType.TEST_PACKAGE_ENDED,
                                 sender = "ots-worker1",
                                 description = "test-newpackage-tests")
        plugin.add_monitor_event(event_package1)
        plugin.set_tested_packages({"env" : ["test-newpackage-tests"]})
        plugin.publish()
        db_package = Package.objects.filter(package_name = "test-newpackage-tests")
        history = History.objects.filter(package_id = db_package[0].id)
        self.assertTrue(db_package.count() == 1)
        self.assertTrue(history.count() == 1)
        self.assertTrue(history[0].duration >= 1)
    
    def testAddToOld(self):
        
        plugin = HistoryPlugin("0001", "0001", "example_product", "no image")
        
        event_package1 = Monitor(event_type = MonitorType.TEST_PACKAGE_STARTED,
                                 sender = "ots-worker1",
                                 description = "test-package1-tests")
        plugin.add_monitor_event(event_package1)
        event_package1 = Monitor(event_type = MonitorType.TEST_PACKAGE_ENDED,
                                 sender = "ots-worker1",
                                 description = "test-package1-tests")
        plugin.add_monitor_event(event_package1)
        plugin.set_tested_packages({"env" : ["test-package1-tests"]})
        plugin.publish()

        db_package = Package.objects.filter(package_name = "test-package1-tests")
        history = History.objects.filter(package_id = db_package[0].id)
        
        self.assertTrue(db_package.count() == 1)
        self.assertTrue(history.count() == 2)
        
    def testNoEndTime(self):
        
        plugin = HistoryPlugin("0001", "0001", "example_product", "no image")
        
        event_package1 = Monitor(event_type = MonitorType.TEST_PACKAGE_STARTED,
                                 sender = "ots-worker1",
                                 description = "test-noenddata-tests")
        plugin.add_monitor_event(event_package1)
        plugin.set_tested_packages({"env" : ["test-noenddata-tests"]})
        plugin.publish()

        db_package = Package.objects.filter(package_name = "test-noenddata-tests")
        
        self.assertTrue(db_package.count() == 0)


class TestDistributionModel(unittest.TestCase):
    """
    Unit tests for distribution model plug-in
    """

    def setUp(self):
        """
        Unit test setup
        """

        _create_test_data()

    def tearDown(self):
        """
        Unit test tear down
        """
        # Deleting all data
        Package.objects.all().delete()
        History.objects.all().delete()

    def _default_options(self):
        
        options = dict()
        options['image_url'] = "none"
        options['testrun_id'] = "123123"
        options['timeout'] = str(500)
        options['emmc_flash_parameter'] = ""
        options['storage_address'] = ""
        options['testfilter'] = ""
        options['flasherurl'] = ""
        options['bootmode'] = ""
        options['use_libssh2'] = False
        
        return options
    
    def testPackagaHistoryTime(self):
        
        packages = ["test-package1-tests",
                    "test-package2-tests",
                    "test-package4-tests"]
        history_times = [60,120,240]
        
        history_data = get_test_package_history(packages)
        for (pkg, duration) in history_data.items():
            for x in range(len(packages)):
                if pkg == packages[x]:
                    self.assertTrue(duration == history_times[x])
    
    def testDistributionModelDevice(self):
        
        options = self._default_options()
        
        packages = "test-package1-tests,test-package2-tests,test-package4-tests"
        
        test_list = dict()
        test_list["device"] = packages
        
        schedule_options = dict()
        schedule_options["target_execution_time"] = 180
        schedule_options["max_worker_amount"] = 2
        
        func = get_model(schedule_options)
        cmds = func(test_list, options)
        
        self.assertTrue(len(cmds) == 2)
        
    def testDistributionModelHost(self):
        
        options = self._default_options()
        
        packages = "test-package1-tests,test-package2-tests,test-package4-tests"
        
        test_list = dict()
        test_list["host"] = packages
        
        schedule_options = dict()
        schedule_options["target_execution_time"] = 180
        schedule_options["max_worker_amount"] = 2
        
        func = get_model(schedule_options)
        cmds = func(test_list, options)
        
        self.assertTrue(len(cmds) == 2)
        
    def testDistributionModelHostDeviceMix(self):
        
        options = self._default_options()
        
        packages = "test-package3-tests,test-package2-tests"
        
        test_list = dict()
        test_list["device"] = packages
        
        packages = "test-package1-tests,test-package4-tests"
        
        test_list["host"] = packages
        
        schedule_options = dict()
        schedule_options["target_execution_time"] = 180
        schedule_options["max_worker_amount"] = 4
        
        func = get_model(schedule_options)
        cmds = func(test_list, options)
        
        self.assertTrue(len(cmds) == 4)
        
    def testDistributionModelHostDeviceMixNoGroupsForHost(self):
        
        options = self._default_options()
        
        packages = "test-package3-tests,test-package2-tests"
        
        test_list = dict()
        test_list["device"] = packages
        
        packages = "test-package1-tests,test-package4-tests"
        
        test_list["host"] = packages
        
        schedule_options = dict()
        schedule_options["target_execution_time"] = 180
        schedule_options["max_worker_amount"] = 2
        
        func = get_model(schedule_options)
        cmds = func(test_list, options)
        
        self.assertTrue(len(cmds) == 3)

class TestSchedulerAlgorithm(unittest.TestCase):
    """
    Unit tests for scheduler
    """
    
    def testPackagesNormal(self):
        
        test_packages = {"test-package1" : 10,
                         "test-package2" : 20,
                         "test-package3" : 30}
        
        groups = group_packages(test_packages, 30, 2)
        
        self.assertTrue(len(groups) == 2)
        self.assertEquals(groups[0][0], "test-package3")
        
    def testPackagesUnknown(self):
        
        test_packages = {"test-package1" : 30,
                         "test-package2" : 30,
                         "test-package3" : None}
        
        groups = group_packages(test_packages, 61, 2)
        self.assertTrue(len(groups) == 2)
        self.assertEquals(groups[1][0], "test-package3")
        
    def testNotEnoughGroups(self):
        
        test_packages = {"test-package1" : 31,
                         "test-package2" : 32,
                         "test-package3" : 33,
                         "test-package4" : 34,
                         "test-package5" : 35,
                         "test-package6" : 36,
                         "test-package7" : 37,
                         }
        
        groups = group_packages(test_packages, 61, 2)
        self.assertTrue(len(groups) == 2)
        self.assertEquals(groups[0][0], "test-package7")
        
    def testMultipleNone(self):
        
        test_packages = {"test-package1" : 120,
                         "test-package2" : 32,
                         "test-package3" : 33,
                         "test-package4" : None,
                         "test-package5" : 35,
                         "test-package6" : None,
                         "test-package7" : 37,
                         }
        
        groups = group_packages(test_packages, 120, 5)
        self.assertTrue(len(groups) == 4)
        self.assertTrue(len(groups[3]) == 2)
        self.assertEquals(groups[0][0], "test-package1")
        self.assertEquals(groups[3][0], "test-package4")
        self.assertEquals(groups[3][1], "test-package6")
    

if __name__ == "__main__":
    unittest.main()