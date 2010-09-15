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
Hackish WIP

Plugins defined here.

Adding a new plugin will allow
safe discovery and instantiation at runtime.

<thinks>
Obfuscation or hiding of implementation details?
</thinks>
"""

from ots.server.hub.application_id import get_application_id
from ots.common.framework.load_plugins import plugin_factory

class PluginMetaclass(type):
    """
    The Plugin Metaclass
    """

    def __new__(cls, name, bases, attrs):
        """
        rtype: L{ots.common.framework.PluginBase} or None
        rparam: creates the plugin if available otherwise None
        """
        klass = plugin_factory(name)
        if klass is not None:
            klass.application_id = get_application_id()
            return klass
        def none(*args): return None
        return none

class BifhPlugin(object):
    """
    The BifhPlugin
    """
    __metaclass__ = PluginMetaclass

class PersistencePlugin(object):
    """
    The PersistencePlugin
    """
    __metaclass__ = PluginMetaclass
