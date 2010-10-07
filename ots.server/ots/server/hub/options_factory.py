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
import yaml

from ots.server.hub.options import Options 

"""
Safely create the Options API from a dictionary 
setting configurable defaults
""" 

def _default_options_dict(sw_product):
    """
    @type sw_product : C{str}
    @param sw_product : The name of the software product
    
    @rtype default_options_dict : C{dict} or None
    @param default_options_dict : The dictionary of options

    Get the default options for the SW product
    """
    #FIXME: This provides the expected interface
    #the implementation requires design decisions
    #to make the extensibility consistent
    dirname = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(dirname, "options_defaults.yaml")
    all_defaults_options_dict = yaml.load(open(file, "r"))
    return all_defaults_options_dict.get(sw_product, {})

def options_factory(sw_product, options_dict):
    """
    @type sw_product : C{str}
    @param sw_product : The name of the software product

    @type options_dict : C{dict}
    @param options_dict: The dictionary of options

    Adapts the options dictionary to the interface 
    Overrides the defaults depending on configuration
    """
    #sanitise the dict (hyphens aren't Python friendly)
    sanitised_options_dict = dict([(k.replace("-","_"), v) 
                                   for k,v in options_dict.items()])
    #Get the defaults for the sw product
    merged_options_dict = _default_options_dict(sw_product)
    #
    merged_options_dict.update(sanitised_options_dict)
    return Options(**merged_options_dict)
