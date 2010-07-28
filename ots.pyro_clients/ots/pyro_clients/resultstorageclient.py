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

"""PostProcessPlugin for fetching results from results storage"""

import Pyro.errors
import Pyro.core

from ots.pyro_clients.postprocessplugin import PostProcessPlugin

class ResultsStorageClient(PostProcessPlugin):
    """PostProcessPlugin for fetching results from results storage"""

    
    def __init__(self, host, port, log, server_proxy = None):
        """Results handler for fetching results from results storage"""    
        self.log = log
        self.hostname = host
        self.port = int(port)
        self.client_initialized = False
        if not server_proxy:
            server_proxy = self._get_server_proxy("results_storage")
        self.server = server_proxy
        self.log.info("ResultsStorageHandler for host %s, port %s initialized"
                      % (str(host), str(port)))


    def name(self):
        """Returns the name of the plugin"""
        return "ResultStorageClient"
 

    def process(self, testrun_object):
        """ Fetches results for a testrun and stores them into testrun_object

        Connects to result storage and fetches result files for the testrun.
        Stores them into testrun object

        Parameters:

            - testrun_object: The testrun object to process

        Returns:

            Nothing

        """
        testrun_id = testrun_object.get_testrun_id()
        results = self._fetch_results(testrun_id)
        for result_file in results:
            testrun_object.add_result_object(result_file)

    def _fetch_results(self, testrun_id):
        """
        Fetches all result files for a testrun. Returns a list of results
        objects.
        """
        try:
            self.log.info("Fetching results for testrun %s" % str(testrun_id))
            results = self.server.get_results(testrun_id)
            self.server.clean_testrun_results(testrun_id)
            self.log.info("Results for testrun %s fetched" % str(testrun_id))
            return results
        except Pyro.errors.ProtocolError:
            self.log.exception("Failed to fetch results for testrun %s"
                               % str(testrun_id))
            return dict()

    def _get_server_proxy(self, service):
        """Gets proxy for service object"""
        
        if not self.client_initialized:
            Pyro.core.initClient()
            self.client_initialized = True

        try:
            uri = 'PYROLOC://%s:%d/%s' % (self.hostname, self.port, service)
            return Pyro.core.getAttrProxyForURI(uri)

        except Pyro.core.PyroError, exception:
            raise Pyro.core.PyroError("Couldn't bind object, Pyro says:",
                                      exception)

