# -*- coding: utf-8 -*-
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

# Modified from the defaultflasher.py by Sampo Saaristo
# Modified to support multiple devices by Esa-Pekka Miettinen
# pylint: disable-msg=W0511


"""
This module includes meego-ai flasher for N900 
"""

from ots.common.framework.api import FlasherPluginBase
from ots.common.framework.api import FlashFailed
from ots.common.framework.api import InvalidImage
from ots.common.framework.api import InvalidConfig
from ots.common.framework.api import ConnectionTestFailed

import logging

class ExampleFlasher(FlasherPluginBase):
    def __init__(self,
                 flasher=None,
                 device_n = None,
                 host_ip = None,
                 device_ip = None,
                 **kwargs):
        """
        @type flasher: C{str}
        @param flasher: Path to flasher
        
        @type device_n: C{int}
        @param device_n: Number of the conductor instance
        
        @type host_ip: C{string}
        @param host_ip: Host IP for flasher
        
        @type device_ip: C{string}
        @param device_ip: Device IP for flasher
        """
        
        super(FlasherPluginBase, self).__init__()

    def flash(self,
              image_path,
              content_image_path,
              boot_mode = None):
        """
        Call this method to start flashing.

        @type image_path: C{string}
        @param image: Absolute path of image file

        @type content_image_path: C{string}
        @param content_image_path: Absolute path of Device content image file

        @type boot_mode: C{string}
        @param boot_mode: Boot mode parameter from ots input parameters.
        
        """

        log = logging.getLogger("example flasher")
        log.info("This is example flasher, flashing....")
