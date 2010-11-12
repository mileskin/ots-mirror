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
A simple forking xmlrpc server for serving the ots public interface
"""

import os
import ConfigParser

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ForkingMixIn

from ots.common.framework.api import config_filename

from ots.server.hub.api import Hub 
from ots.server.hub.api import get_application_id

from ots.server.distributor.api import TaskRunner

################################
# HACKISH TESTING CAPABILITIES
################################

DEBUG = False

if DEBUG:
    from ots.server.hub.tests.component.mock_taskrunner import \
                                       MockTaskRunnerResultsPass
    
###########################
# OTS FORKING SERVER
###########################

class OtsForkingServer(ForkingMixIn, SimpleXMLRPCServer):
    pass

def _config():
    """
    rtype: C{Tuple) of C{str} and C{str}
    rparam: hostname, port
    """
    server_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    app_id = get_application_id() 
    conf = config_filename(app_id, server_path)
    config = ConfigParser.ConfigParser()
    config.read(conf)       
    return config.get('ots.server.xmlrpc', 'host'), \
           int(config.get('ots.server.xmlrpc', 'port'))



#############################
# REQUEST_SYNC
#############################

def request_sync(sw_product, request_id, notify_list, options_dict):
    """
    Convenience function for the interface for the hub.
    Processes the raw parameters and fires a testrun

    @type sw_product: C{str}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{str}
    @param request_id: An identifier for the request from the client

    @type notify_list: C{list}
    @param notify_list: Email addresses for notifications

    #FIXME legacy interface 
    @type options_dict: C{dict}
    @param options_dict: A dictionary of options
    """
    options_dict["notify_list"] = notify_list
    hub = Hub(sw_product, request_id, **options_dict)
    if DEBUG:
        hub._taskrunner = MockTaskRunnerResultsPass()
    return hub.run()
    
def main():
    """
    Top level script for XMLRPC interface
    """
    server = OtsForkingServer(_config(), SimpleXMLRPCRequestHandler)
    server.register_function(request_sync)
    print "Starting OTS xmlrpc server..."
    print 
    print "Host: %s, Port: %s" % _config()
    server.serve_forever()

if __name__ == "__main__":
    main()
