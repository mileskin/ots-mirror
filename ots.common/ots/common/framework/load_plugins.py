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

from pkg_resources import Environment, working_set

LOG = logging.getLogger(__name__)

def plugins_iter(plugin_dir, ep_name):
    """
    @type plugin_dir : C{str}
    @param plugin_dir : The fqname of the plugin directory 

    @type ep_name : C{str}
    @param ep_name : The name of the Entry Point to be loaded 
    
    @ytype : C{obj}
    @yparam : The loaded Entry Point 
    """
    #TODO review this code
    working_set.add_entry(plugin_dir)
    pkg_env = Environment([plugin_dir])
    plugins={}
    for env_name in pkg_env:
        egg = pkg_env[env_name][0]
        LOG.debug("Activating egg: %s"%(egg))
        egg.activate()
        for name in egg.get_entry_map(ep_name):
            entry_point = egg.get_entry_info(ep_name, name)
            LOG.debug("Loading entry point: %s"%(entry_point))
            cls = entry_point.load()
            yield cls
    for entry_point in working_set.iter_entry_points(ep_name):
        LOG.debug("Loading entry point: %s"%(entry_point))
        cls = entry_point.load()
        yield cls
