# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
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


"""
Provides Class based access to Schema definition
"""

import configobj
from ots.server.server_config_filename import server_config_filename

SCHEMA_FILENAME = configobj.ConfigObj(server_config_filename())\
                  ["ots.results"]["results_xsd"]

TRUE = "true"
FALSE = "false"

class Names(object):
    """
    Names of the Schema Tags as Defined in the XSD
    """

    INSIGNIFICANT = "insignificant"
    RESULT = "result"
