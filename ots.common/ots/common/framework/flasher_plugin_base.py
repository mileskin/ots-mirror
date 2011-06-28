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

""" Interface class for flasher plug-ins """

# Example flasher, disable pylint warnings 
# pylint: disable=W0613

import logging

LOG = logging.getLogger("default_flasher")


class FlashFailed(Exception):
    """Flash Failed exception"""
    pass

class InvalidImage(Exception):
    """Invalid Image exception"""
    pass

class InvalidConfig(Exception):
    """Invalid configuration exception"""
    pass

class ConnectionTestFailed(Exception):
    """Connection test failed exception"""
    pass


class FlasherPluginBase(object):
    """ Default class for SoftwareUpdater """

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

        @type image_path: C{str}
        @param image_path: Absolute path of image file

        @type content_image_path: C{str}
        @param content_image_path: Absolute path of Device content image file

        @type boot_mode: C{str}
        @param boot_mode: Boot mode parameter from ots input parameters.
        """

        LOG.warning("***************************************************")
        LOG.warning("* Customflasher not available in Worker!          *")
        LOG.warning("* Setting up test target cannot be done.          *")
        LOG.warning("* You must implement customflasher Python         *")
        LOG.warning("* module (see OTS Worker documentation).          *")
        LOG.warning("* Now continuing as if test target is set up...   *")
        LOG.warning("***************************************************")

    def clean_up(self):
        """
        This method is called after the test execution is done
        or error has occurred.
        """
        LOG.warning("Nothing to clean up")
