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

import sys

import logging

from django.utils import simplejson
from django.http import HttpResponse

LOG = logging.getLogger(__name__)

class JSONRPCService: 

    def __init__(self, method_map={}):
        LOG.debug("Initialising JSONRPCService") 
        self.method_map = method_map
	
    def add_method(self, name, method):
        self.method_map[name] = method
        LOG.debug("Adding JSONRPCService method %s"%(method))
		
    def __call__(self, request, extra=None):
        data = simplejson.loads(request.raw_post_data)
        id = data["id"]
        method = data["method"]
        params = [request,] + data["params"]
        if method in self.method_map:
            LOG.debug("__call__ method '%s' with params '%s'"%(method, 
                                                               data["params"]))
            result = self.method_map[method](*params)
            #This is the recommended pyjamas-django integration thru jsonrpc
            #But it doesn't appear to support connecting handlers to callers
            #other than onRemoteReponse.
            #Hacking for now
            response = simplejson.dumps({'id': id, 'result': (method, result)})
        else:
            LOG.debug("No registered method '%s'"%(method))
            response = simplejson.dumps({'id': id, 
                                         'error': "No such method", 'code': -1})
        return HttpResponse(response)


def jsonremote(service):
    """
    JSONRPC decorator
    """
    def remotify(func):
        LOG.debug("jsonremote: '%s'"%(func.__name__))
        if isinstance(service, JSONRPCService):
            service.add_method(func.__name__, func)
        else:
            raise NotImplementedError, 'Service "%s" not found' \
                                              % str(service.__name__)
        return func

    return remotify

