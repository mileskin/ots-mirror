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


class Options(object):
    """A mock for ots_trigger options"""

    def __init__(self):
        # Default call options
        self.id = 0
        self.engine = ""
        self.image = "http://dontcareabouttheimage"
        self.engine = "default"
        self.testpackages = []
        self.hosttest = []
        self.distribution = "default"
        self.filter = ""
        self.input_plugin = ""
        self.device = ""
        self.sw_product = "default"
        self.email = "tvainio@localhost"
        self.timeout = 30
        self.server = "%s/xmlrpc" % SERVER # TODO: To cmd line parameters

    pass

class TestErrorConditions(unittest.TestCase):

    def test_non_existing_devicegroup(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist"
        options.timeout = 1
        print "Triggering a testrun with non existing devicegroup '%s'"\
            % options.device
        print "Please make sure the system does not have that devicegroup."

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

    def test_non_existing_sw_product(self):
        options = Options()
        options.sw_product = "this_should_not_exist"
        options.timeout = 1
        print "Triggering a testrun with non existing sw_product '%s'"\
            % options.sw_product
        print "Please make sure the system does not have that sw_product."

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        self.assertTrue(has_errors(testrun_id))
        string = """Unknown sw_product this_should_not_exist"""
        self.assertTrue(has_message(testrun_id, string))

        string = """Incoming request: program: this_should_not_exist, request: 0, notify_list: ['tvainio@localhost'], options: {'engine': ['default'], 'image': 'http://dontcareabouttheimage', 'distribution_model': 'default', 'timeout': 1}"""
        self.assertTrue(has_message(testrun_id, string))

class TestDeviceProperties(unittest.TestCase):

    def test_multiple_devicegroups(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist;devicegroup:this_should_not_exist_either"
        options.timeout = 1
        print "Calling ots xmlrpc with multiple devicegroups: '%s'"\
            % options.device
        print "Please make sure the system does not have these devicegroups."
        print "Checking that a separate testrun gets created for all devicegroups."
        
        old_testrun = get_latest_testrun_id()
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "FAIL")

        testrun_id1 = get_second_latest_testrun_id()        
        testrun_id2 = get_latest_testrun_id()


        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(testrun_id1))
        self.assertTrue(has_errors(testrun_id2))
        
        # Make sure correct routing keys are used
        string = """Using routing key this_should_not_exist"""
        self.assertTrue(has_message(testrun_id1, string))

        string = """Using routing key this_should_not_exist_either"""
        self.assertTrue(has_message(testrun_id2, string))

        string = """'device': {'devicegroup': 'this_should_not_exist'}"""

        self.assertTrue(has_message(testrun_id1, string))

        string = """'device': {'devicegroup': 'this_should_not_exist_either'}"""
        self.assertTrue(has_message(testrun_id2, string))


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
def get_second_latest_testrun_id():
    """
    Scrape the second latest testrun id from the global log
    """
    latest = get_latest_testrun_id()
    file =  urllib2.urlopen("%s"% GLOBAL_LOG)
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for row in rows:
        if row.findAll("td"):
            td = row.findAll("td")[0].string
            if td != latest:
                return td
    return None

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
                elif td[4].string == None: # Check also <pre> messages </pre>
                    if td[4].findAll("pre")[0].string.count(string):
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
