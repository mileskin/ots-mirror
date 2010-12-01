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

"""
OTS log based system tests.

These tests expect that you have full ots system set up. They trigger testruns
and check http logs for expected results

Make sure there is no other activities going on in the system while running 
the tests!

"""

import unittest
import urllib2
from BeautifulSoup import BeautifulSoup
from ots.tools.trigger.ots_trigger import ots_trigger
SERVER = "localhost"
GLOBAL_LOG = "http://%s/logger/view/" % (SERVER)
EMAIL = "tvainio@localhost"

class Options(object):
    pass

class TestErrorMessages(unittest.TestCase):

    def test_non_existing_devicegroup(self):
        options = Options()
        options.id = 0
        options.engine = None
        options.image = "http://dontcareabouttheimage"
        options.engine = "default"
        options.testpackages = []
        options.hosttest = []
        options.distribution = "default"
        options.filter = ""
        options.input_plugin = ""
        options.device = "devicegroup:this_should_not_exist"
        options.sw_product = "default"
        options.email = EMAIL
        options.timeout = 1
        options.server = "%s/xmlrpc" % SERVER # TODO: To cmd line parameters
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "FAIL")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assertTrue(has_message(testrun_id, string))

        string = """Queue 'this_should_not_exist' does not exist"""
        self.assertTrue(has_message(testrun_id, string))

        string = 'error_info set to "Queue \'this_should_not_exist\' does not exist"'
        self.assertTrue(has_message(testrun_id, string))
        string = """ncoming request: program: default, request: 0, notify_list: ['tvainio@localhost'], options: {'engine': ['default'], 'device': {'devicegroup': 'this_should_not_exist'}, 'image': 'http://dontcareabouttheimage', 'distribution_model': 'default', 'timeout': 1}"""
        self.assertTrue(has_message(testrun_id, string))



##################################
# Helper functions for log parsing
#
def get_latest_testrun_id():
    """
    Scrape the latest testrun id from the global log
    """
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    row1 = table.findAll("tr")[1]
    td = row1.findAll("td")[0].string
    return td

def has_message(testrun_id, string):
    """
    Tries to find a message in the log for the given testrun
    Returns True if message was found
    """
    ret_val = False
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            if td[0].string == testrun_id:
                if td[4].string and td[4].string.count(string):
                    ret_val = True
                    break

    return ret_val

def has_errors(testrun_id):
    """
    Checks if testrun has any error messages
    """
    ret_val = False
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        error = ""
        td = tr.findAll("td")
        if td:

            if td[0].string == testrun_id:
                # "ERROR" has some styling around it:
                try:
                    error  =  td[3].findAll("div")[0].findAll("b")[0].string
                except IndexError:
                    pass
                if error == "ERROR":
                    ret_val = True
                    break
    return ret_val


if __name__ == "__main__":
    unittest.main()
