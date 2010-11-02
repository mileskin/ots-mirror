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

import pkg_resources

LOG = logging.getLogger(__name__)

def plugins_iter(plugin_dir, entry_point):
    """
    @type plugin_dir : C{str}
    @param plugin_dir : The fqname of the plugin directory 

    @type entry_point : C{str}
    @param entry_point : The Entry Point to be loaded 
    
    @ytype : C{obj}
    @yparam : The loaded Entry Point 
    """
    pkg_resources.working_set.add_entry(plugin_dir)
    pkg_env=pkg_resources.Environment([plugin_dir])
    plugins={}
    for name in pkg_env:
        egg=pkg_env[name][0]
        LOG.debug("Activating egg: %s"%(egg))
        egg.activate()
        modules=[]
        for name in egg.get_entry_map(entry_point):
            entry_point=egg.get_entry_info(entry_point, name)
            LOG.debug("Loading entry point: %s"%(entry_point))
            cls=entry_point.load()
            yield cls
