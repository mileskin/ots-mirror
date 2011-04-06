# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
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

"""
A simple forking xmlrpc server for serving the ots public interface
"""

import sys
import configobj
import logging

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ForkingMixIn
from ots.server.server_config_filename import server_config_filename
from ots.server.xmlrpc.public import request_sync

###########################
# OTS FORKING SERVER
###########################

class OtsForkingServer(ForkingMixIn, SimpleXMLRPCServer):
    """ Fork class for XMLRPC server """
    pass

def _config():
    """
    @rtype: C{tuple} of C{str} and C{int}
    @return: hostname, port
    """
    config_file = server_config_filename()
    config = configobj.ConfigObj(config_file).get("ots.server.xmlrpc")
    return config.get('host'), config.as_int('port')


def main(is_logging = False):
    """
    Top level script for XMLRPC interface
    """
    server = OtsForkingServer(_config(), SimpleXMLRPCRequestHandler)
    server.register_function(request_sync)
    print "Starting OTS xmlrpc server..."
    print
    print "Host: %s, Port: %s" % _config()
    print

    if is_logging:
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(log_handler)

    server.serve_forever()

if __name__ == "__main__":
    SHOW_LOGGING = False
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        SHOW_LOGGING = True
    main(SHOW_LOGGING)
