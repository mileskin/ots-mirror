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
Simple Context Manager 
"""

import traceback
import logging 

LOG = logging.getLogger(__name__)

class plugin_exception_policy:
    """
    Plugin Exception Policy 
    currently on or off
    """
    def __init__(self, swallow = True):
        self.swallow = swallow

    def __enter__(self):
        pass

    def __exit__(self, exception_type, value, tb):
        if exception_type is not None:
            LOG.warning("Error in plugin", exc_info=(exception_type, value, tb))
            if self.swallow:
                LOG.debug("Ignoring plugin error")
        return self.swallow 
