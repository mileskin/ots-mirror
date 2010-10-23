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

import logging

from pkg_resources import working_set, Environment

LOG = logging.getLogger(__name__)

def _find_plugins(plugin_dir):
    """
    @type plugin_dir: C{str}
    @param plugin_dir: The path name of the plugin directory

    @rtype: C{list} of C{pkg_resources.Distribution}
    @rparam: A list of plugins
    """

    env = Environment([plugin_dir])
    plugins, errors =  working_set.find_plugins(env)
    if errors:
        LOG.debug("Error finding plugins: %s"%(errors))
    return plugins

def load_plugins(plugin_dir):
    """
    @type plugin_dir: C{str}
    @param plugin_dir: The path name of the plugin directory
    """
    for package in _find_plugins(plugin_dir):
        LOG.debug("Activating: '%s'"%(package.egg_name()))
        working_set.add(package)

def plugin_factory(name):
    """
    @type name: C{str}
    @param name: The name of the plugin

    @rtype: C{klass}
    @rparam: The Plugin Klass
    """
    ret_val = None
    try:
        entry_point = working_set.iter_entry_points(name).next()
        LOG.debug("Loading module '%s'"% (entry_point))
        module = entry_point.load()
        if hasattr(module, name):
            ret_val = getattr(module, name)
        else:
            LOG.debug("%s has no attribute %s"%(module, name))
    except StopIteration:
        LOG.debug("No entry point: %s"%(name))
    return ret_val
