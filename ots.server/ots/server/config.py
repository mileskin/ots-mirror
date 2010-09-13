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
Config file handling code for ots server
"""
import os


DEFAULT_CONFIG_FILE = "/etc/ots-server.ini"
def config_file_name():
    """
    Returns the config file path.

    Tries /etc/ots-server.ini first. If that doesn't exist it tries config.ini
    from ots.server directory
    """
    if os.path.exists(DEFAULT_CONFIG_FILE):
        return DEFAULT_CONFIG_FILE

    distributor_dirname = os.path.dirname(os.path.abspath(__file__))
    distributor_config_filename = os.path.join(distributor_dirname,
                                               "config.ini")
    if not os.path.exists(distributor_config_filename):
        raise Exception("%s not found"%(distributor_config_filename))
    return distributor_config_filename
