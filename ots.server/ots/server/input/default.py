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

"""Default input plugin. Only logs all actions"""

import logging
from ots.common.interfaces.inputplugin import InputPlugin

class Default(InputPlugin):
    """Default input plugin. Only logs all actions"""


    def __init__(self):
        """
        Constructor
        
        """
        self.log = logging.getLogger(__name__)


    def get_changed_packages(self, build_id):
        """
        Returns empty list
        """
        self.log.debug("get_changed_packages called for build: %s" % build_id)
        return []

    def store_url(self, url, text):
        """ 
        logs url
        """  

        self.log.debug("store_url called: %s: %s " % (url, text))

    def store_file(self,
                   file_content,
                   filename,
                   label,
                   description):
        """ 
        Logs filename
        """  
        
        self.log.debug("store_file called for file: %s" % filename)
