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

import os

DEFAULT_CONFIG_FILEPATH = "/etc/"

class ConfigException(Exception):
    pass

def config_filename(application_id = None, path = None):
    """
    Returns the configuration file 
    and checks that it exists.

    1. /DEFAULT_CONFIG_FILEPATH/APPLICATION_ID.ini 
    2. If application_id and path are specified use that
    3. Use config.ini from ots.common directory #FIXME
    
    @type application_id: C{str}
    @param application_id : The identifier for the OTS application

    @type path: C{str}
    @param path: The path 
 
    @rtype: C{str}
    @rparam the fully qualified config file path.
    """    
    if application_id is not None:
        name = "%s.ini" % (application_id)
    else:
        name = "config.ini"
    #
    default = os.path.join(DEFAULT_CONFIG_FILEPATH, name)
    if os.path.exists(default):
        config_filename = default
    elif path is not None:
        config_filename = os.path.join(path, name)
    else:
        common_dirname = os.path.split(os.path.dirname(
                           os.path.abspath(__file__)))[0]
        config_filename = os.path.join(common_dirname, name)
    #
    if not os.path.exists(config_filename):
        raise ConfigException("Can't find config in '%s' or '%s'"% \
                               (default, config_filename))
    return config_filename
