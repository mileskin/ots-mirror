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

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ForkingMixIn
from ots.server.xmlrpc.public import request_sync

try:    
    from ots_extensions import ots_config
except ImportError: # If no custom config found, use the default
    from ots.server.testrun_host import default_ots_config as ots_config



class OtsForkingServer(ForkingMixIn, SimpleXMLRPCServer):
    pass


def main():

    config = (ots_config.xmlrpc_host, ots_config.xmlrpc_port)
    server = OtsForkingServer(config, SimpleXMLRPCRequestHandler)
    server.register_function(request_sync)
    print "Starting OTS xmlrpc server..."
    print 
    print "Using config file %s" % ots_config.__file__
    print "Host: %s, Port: %s" % config
    server.serve_forever()

if __name__ == "__main__":
    main()
