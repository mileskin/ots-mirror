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

"""Results storage service"""

import logging
import Pyro.core
from Pyro.ext import remote_nons
from ots.pyro_services.results_storage import resultobject
import sys
import datetime
import time
from socket import gethostname




DEFAULTHOST = "localhost"
DEFAULTPORT = 1982
CLEANUPPERIOD = 1 * 24 * 60 * 60 # one day in seconds
LOG_FILENAME = "results_storage_service.log"






class ResultsStorage(Pyro.core.SynchronizedObjBase):
    """
    Results storage service. Result files can be stored and retrieved
    from it.
    """
    def __init__(self, config, host, port):
        """
        Results storage object. Config is a dictionary based on config file.
        Host and port are for the Pyro service object. They are only used
        for logging etc.
        """
        Pyro.core.SynchronizedObjBase.__init__(self)
        self.testruns = dict()
        self.host = host
        self.port = port
        self.cleanup_period = config['cleanup_period']
        self.log = logging.getLogger(__name__)
        self.log.info("Creating results storage object")
        self.starttime = datetime.datetime.now()
    
    def info(self):
        """Returns general information about the service."""
        return "OTS Results Storage Service running at "+self.host

    def status(self):
        """Returns status of the storage."""
        return """Service started: %s\nTestruns in memory: %s\nTotal result files in memory: %s\n"""\
        % (str(self.starttime), len(self.testruns), self._count_result_files())




# Api for worker:

    def add_result(self, testrun_id, file_name, file_content, origin="Unknown",
                   testpackage="Unknown", environment="Unknown"):
        """
        Stores result file for testrun_id. If filename already
        exists it will be overwritten.
        origin is the host name of the client who produced the result file.
        environment is hardware/scratchbox/host
        """
        try:
            testrun_id = str(testrun_id)
            if not testrun_id in self.testruns:
                self.testruns[testrun_id] = []
            result = resultobject.ResultObject(file_name, file_content,
                                             testpackage, origin, environment)
            self.testruns[testrun_id].append(result)
            self.log.info("added resultfile %s. Testrun id: %s, Testpackage: %s \
             origin: %s, Test environment: %s" % (file_name, testrun_id,
                                                  testpackage, origin,
                                                  environment))
        except:
            self.log.exception("add_result() failed: testrun_id %s, file %s"% (str(testrun_id), str(file_name)))


    def add_results_object(self, testrun_id, results_object):
        """
        Stores result file object for testrun_id. If filename already
        exists it will be overwritten.
        """
        try:
            testrun_id = str(testrun_id)
            if not testrun_id in self.testruns:
                self.testruns[testrun_id] = []
            self.testruns[testrun_id].append(results_object)
            self.log.info("added resultfile %s. Testrun id: %s, Testpackage:"\
                              "%s origin: %s, Test environment: %s"\
                              % (results_object.name(),
                                 testrun_id,
                                 results_object.get_testpackage(),
                                 results_object.get_origin(),
                                 results_object.get_environment()))
        except:
            self.log.exception("add_result_object() failed: testrun_id "+str(testrun_id))

# Api for ots server:

    def get_results(self, testrun_id):
        """Returns all result files for a testrun as a list of resultobjects."""

        # TODO: Cleanup is temporarily triggered here. It will be triggered
        # from outside after more new ots components are implemented.
        self._cleanup() 

        testrun_id = str(testrun_id)
        try:
            results =  self.testruns[testrun_id]
            self.log.info("Sent results for testrun "+testrun_id)
            return results
        except KeyError:
            self.log.info("No results available for testrun "+testrun_id)
            return []
        except:
            self.log.exception("Error in get_results() for testrun "+testrun_id)
            return []


    def clean_testrun_results(self, testrun_id):
        """Cleans testrun results from memory"""
        testrun_id = str(testrun_id)
        try:
            del self.testruns[testrun_id]
            self.log.info("Cleaned testrun "+testrun_id+" from memory.")
        except KeyError:
            self.log.info("clean_testrun_results failed: Testrun "+testrun_id+" not in memory.")
        except:
            self.log.exception("Error in clean_testrun_results() for testrun "+testrun_id)



    def clean_files_older_than(self, hours):
        """removes files older than hours"""
        seconds = hours*360
        for key in self.testruns.keys():
            testrun = self.testruns[key]
            for result in testrun:
                if int(result.get_timestamp()) < int(time.time()) - int(seconds):
                    filename = result.name()
                    testrun.remove(result)
                    self.log.info("Removed timeouted resultfile %s for testrun %s" % (filename, key))
                    if len(testrun) == 0:
                        del self.testruns[key]
                        self.log.info("Removed timeouted old testrun %s" % (key))

    def _count_result_files(self):
        """Counts result files currently stored"""
        count = 0
        for testrun in self.testruns.values():
            count = count + len(testrun)

        return count

    def _cleanup(self):
        """Cleans files older than cleanup_period defined in config"""
        try:
            self.clean_files_older_than(self.cleanup_period)
        except:
            self.log.exception("Cleanup failed")



def start_service():
    """Starts the result storage service"""
    log = logging.getLogger("results_storage")
    try:
        serverhost = gethostname()
        serverport = DEFAULTPORT
    except (IndexError, ValueError):
        log.error("could not resolve hostname. Using %s" % DEFAULTHOST)
        serverhost = DEFAULTHOST
        serverport = DEFAULTPORT


    config = dict()
    config['cleanup_period'] = 24
    log.info("Starting OTS results storage service, host %s, port %d"
              % (serverhost, serverport))
    log.info('Providing local server object as "results_storage"...')
    remote_nons.provide_server_object(ResultsStorage(config,
                                                     serverhost,
                                                     serverport)
                                      , 'results_storage', serverhost,
                                      serverport)
    log.info("Waiting for requests...")
    sys.exit(remote_nons.handle_requests())


if __name__ == "__main__":
    log_format = '%(asctime)s  %(name)-12s %(levelname)-12s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename=LOG_FILENAME,
                        format=log_format)
    start_service()
