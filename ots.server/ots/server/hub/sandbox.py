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
sandbox decorator
"""

import sys
import logging

LOG = logging.getLogger(__name__)

LOG.info("Initialising sandbox")

class sandbox(object):
    """
    Decorator that catches all 
    caches the exc_info 
    and returns the given return value 
    Switchable with the `is_on` parameter
    """

    is_on = True
    exc_info = (None, None, None)

    def __init__(self, ret_val):
        """
        @type ret_val : N/A
        @param ret_val : The default ret_val if an exception is raised
        """
        self._ret_val = ret_val

    def __call__(self, func):
        """
        @type func : C{callable}
        @param func : The function being decorated
        """
        def sandboxed_func(*args):
            try:
                return func(*args)
            except:
                if sandbox.is_on:
                    if sandbox.exc_info == (None, None, None):
                        LOG.exception("sandbox caught error")
                        sandbox.exc_info = sys.exc_info()
                    return self._ret_val
                else:
                    raise
        return sandboxed_func
