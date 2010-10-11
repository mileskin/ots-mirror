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
import unittest
import datetime
from ots.server.testrun_db import interface
from ots.server.testrun_db import models
from ots.common.testrun import Testrun

from django.test.utils import setup_test_environment
setup_test_environment()

class TestInterface(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_init_new_testrun(self):
        swproduct = "meego_1"
        testrun_id = interface.init_new_testrun(swproduct = swproduct)
        db_testrun = models.Testrun.objects.get(id=testrun_id)
        self.assertEquals(db_testrun.swproduct, swproduct)

    def test_update_testrun(self):
        swproduct = "meego_1"
        testrun_id = interface.init_new_testrun(swproduct = swproduct)
        testrun_object = Testrun()

        state = "FINISHED"
        status_info = "yes, it really is finished!"
        testrun_object.set_state(state, status_info)

        image_url = "http://dummyurl"
        testrun_object.set_image_url(image_url)

        build_id = "5"
        testrun_object.set_request_id(build_id)

        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(hours=1)
        testrun_object.starttime = starttime
        testrun_object.endtime = endtime


        result = "ERROR"
        error_code = "1969"
        error_info = "meltdown"
        testrun_object.set_result(result)
        testrun_object.set_error_code(error_code)
        testrun_object.set_error_info(error_info)

        interface.update_testrun(testrun_object, testrun_id)

        db_testrun = models.Testrun.objects.get(id=testrun_id)
        self.assertEquals(db_testrun.state, state)
        self.assertEquals(db_testrun.status_info, status_info)
        self.assertEquals(db_testrun.imageurl, image_url)
        self.assertEquals(db_testrun.build_id, build_id)
        self.assertEquals(db_testrun.starttime, starttime)
        self.assertEquals(db_testrun.endtime, endtime)
        self.assertEquals(db_testrun.result, result)
        self.assertEquals(db_testrun.error_code, error_code)
        self.assertEquals(db_testrun.error_info, error_info)



    def test_add_testrun_link(self):
        testrun_id = interface.init_new_testrun(swproduct = "swproduct")
        url = "http://url.to/results"
        description = "Results for Testrun in an external system"
        interface.add_testrun_link(testrun_id, url, description)
        db_testrun = models.Testrun.objects.get(id=testrun_id)
        stored_links = db_testrun.link_set.all()
        self.assertEquals(len(stored_links), 1)
        self.assertEquals(stored_links[0].url, url)
        self.assertEquals(stored_links[0].description, description)

    def test_get_testrun_link(self):
        testrun_id = interface.init_new_testrun(swproduct = "swproduct")
        url = "http://url.to/results"
        description = "Results for Testrun in an external system"
        interface.add_testrun_link(testrun_id, url, description)
        stored_link = interface.get_testrun_link(testrun_id)
        self.assertEquals(stored_link, url)


if __name__ == '__main__':
    unittest.main()
