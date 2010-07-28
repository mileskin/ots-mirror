#!/usr/bin/env python


# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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


"""Info service"""
import logging
import Pyro.core
import datetime
import time

class InfoService(Pyro.core.SynchronizedObjBase):
    """
    Info Service. Provides a service for distributing info about testruns.
    (status etc.)
    """

    # Disabling "too many public methods" warning.
    # Pyro Base class has many objects and pylint complains even though
    # this class does not have that many public methods 
    # 
    # pylint: disable-msg=R0904
    
    
    def __init__(self, config, host, port):
        
    # Disabling "Unused argument" warning.
    # config is defined in Service interface 
    # 
    # pylint: disable-msg=W0613   
        Pyro.core.SynchronizedObjBase.__init__(self)
        self.host = host
        self.port = port
        self.testruns = dict()
        self.log = logging.getLogger(__name__)
        self.log.info("Creating InfoService Object")
        self.starttime = datetime.datetime.now()
        self.cleanup_period = config['cleanup_period']
#
# General service methods
#
    
    def info(self):
        """Returns general information about the service."""
        return "Info Service running at "+self.host

    def status(self):
        """Returns status of the storage."""
        return """Service started: %s\nTestruns in memory: %s\n"""\
        % (str(self.starttime), len(self.testruns))


#
# API for handling testrundata objects
#


    def add_testrun(self, testrun):
        """Add new testrun to service"""
        
        testrun_id = testrun.get_testrun_id()
        if not testrun_id:
            raise ValueError
        self.testruns[testrun_id] = testrun
            
        
    def get_testrun(self, testrun_id):
        """
        Returns TestrunData object for the id.
        Returns None if id does not exist.
        """
        testrun = None
        try:
            testrun = self.testruns[int(testrun_id)]
        except KeyError:
            self.log.error("get_testrun() failed. Unknown testrun %s" 
                            % str(testrun_id))
        return testrun



    def remove_testrun(self, testrun_id):
        """Cleans testrun from memory."""
        testrun_id = str(testrun_id)
        try:
            del self.testruns[int(testrun_id)]
            self.log.info("Cleaned testrun %s from memory." % testrun_id)
        except KeyError:
            self.log.info("remove_testrun failed: Testrun %s not in memory." 
                            % testrun_id)
        except:
            self.log.exception("Error in remove_testrun for testrun %s"
                            % testrun_id)



    def clean_testruns_older_than(self, hours):
        """removes testruns older than hours"""
        seconds = hours*360
        for key in self.testruns.keys():
            if self.testruns[key].get_creation_time() < time.time() - seconds:
                del self.testruns[key]

    def _cleanup(self):
        """Cleans testruns older than cleanup_period defined in config"""
        try:
            self.clean_testruns_older_than(self.cleanup_period)
        except:
            self.log.exception("Cleanup failed")


#
# API for handling testpackagedata objects in testrun
#


    def add_package_data(self, testrun_id, test_package, data):
        """Stores TestPackageData object into testrun"""
        self.testruns[int(testrun_id)].add_package_data(test_package, data)

    def get_all_package_data(self, testrun_id):
        """Returns all testpackagedata objects for a testrun as a dictionary"""
        return self.testruns[int(testrun_id)].get_all_package_data()


#
# API for getting and updating state of the testrun
#

        
    def get_state(self, testrun_id):
        """
        Returns testrun state and status info as a tuple of strings. 
        Possible state values:
        NOT_STARTED,
        QUEUED,
        TESTING,
        FLASHING,
        STORING_RESULTS,
        FINISHED

        Returns None if testrun is not found.             
        """
        
        try:
            return (self.testruns[int(testrun_id)].get_state(), 
                    self.testruns[int(testrun_id)].get_status_info())
        except KeyError:
            self.log.error("get_state() failed. Unknown testrun %s" 
                            % str(testrun_id))
            return None
        
        
    def set_state(self, testrun_id, state, status_info=""):
        """
        Sets state of the testrun.
        """

        try:
            self.testruns[int(testrun_id)].set_state(state)
            self.testruns[int(testrun_id)].set_status_info(status_info)
        except ValueError:
            self.log.error("Tried to set invalid state %s for testrun %s" 
                            % (str(state), str(testrun_id)))
            raise
        except KeyError:
            self.log.error("Tried to set state for unknown testrun %s" 
                            % (str(testrun_id)))
            raise


#
# API for getting list of all test packages executed by worker
#

    def get_all_executed_packages(self, testrun_id):
        """
        Returns all test packages that the worker reported as to be executed.
        """
        testrun_id = int(testrun_id)
        try:
            return self.testruns[testrun_id].get_all_executed_packages()
        except KeyError:
            self.log.error("info.get_executed_packages() failed. "\
                           "Unknown testrun %s" % str(testrun_id))
            return None

#
# API for getting and setting result and error_info of the testrun
#

    def get_result(self, testrun_id):
        """
        Returns testrun result. Possible values are:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')

        Returns None if testrun is not found.
        """
        self.log.debug("info.get_result() called for testrun %s" 
                        % str(testrun_id))
        try:
            return self.testruns[int(testrun_id)].get_result()
        except KeyError:
            self.log.error("info.get_result() failed. Unknown testrun %s" 
                            % str(testrun_id))
            return None

    def set_result(self, testrun_id, result):
        """
        Set testrun result. Possible values:
        ('NOT_READY','PASS','FAIL','NO_CASES','ERROR')
        """
        try:
            self.testruns[int(testrun_id)].set_result(result)
        except ValueError:
            self.log.error("Tried to set invalid result %s for testrun %s" 
                            % (str(result), str(testrun_id)))
            raise
        except KeyError:
            self.log.error("Tried to set result for unknown testrun %s" 
                            % (str(testrun_id)))
            raise

    def get_error_info(self, testrun_id):
        """
        Returns error info string.
        Returns None if testrun is not found.
        """
        self.log.debug("info.get_error_info() called for testrun %s" 
                        % str(testrun_id))
        try:
            return self.testruns[int(testrun_id)].get_error_info()
        except KeyError:
            self.log.error("info.get_error_info() failed. Unknown testrun %s" 
                            % str(testrun_id))
            return None

    def get_error_code(self, testrun_id):
        """
        Returns error_code.
        Returns None if testrun is not found.
        """
        self.log.debug("info.get_error_code() called for testrun %s" 
                        % str(testrun_id))
        try:
            return self.testruns[int(testrun_id)].get_error_code()
        except KeyError:
            self.log.error("info.get_error_code() failed. Unknown testrun %s" 
                            % str(testrun_id))
            return None

    def set_result_to_error(self, testrun_id, error_code="", error_info=""):
        """
        Sets testrun result to ERROR together with error_info and error_code.
        First error is kept and subsequent calls have no effect.
        """
        testrun_id = int(testrun_id)
        if self.get_result(testrun_id) != "ERROR":
            self.set_result(testrun_id, 'ERROR')
            try:
                self.testruns[testrun_id].set_error_info(error_info)
                self.testruns[testrun_id].set_error_code(error_code)
            except KeyError:
                self.log.error("Tried to set error info and error code for "\
                                "unknown testrun %s" % (str(testrun_id)))
                raise


    def add_executed_packages(self, testrun_id, environment, packages):
        """
        Stores a new list of test packages that are to be executed.
        """
        testrun_id = int(testrun_id)
        try:
            self.testruns[testrun_id].add_executed_packages(environment, 
                                                            packages)
        except KeyError:
            self.log.error("Tried to add executed packages for "\
                            "unknown testrun %s" % (str(testrun_id)))
            raise

