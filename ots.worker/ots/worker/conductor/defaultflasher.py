# -*- coding: utf-8 -*-
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
This module includes simple reference implementation of SoftwareUpdater
"""

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


class SoftwareUpdater(object):
    """ Default class for SoftwareUpdater """
    def flash(self, image_path, content_image_path):
        pass
