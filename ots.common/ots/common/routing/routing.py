#!/usr/bin/python -tt

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

"This module contains components for defining routing keys"

import logging
LOGGER = logging.getLogger(__name__)

                
def get_routing_key(values):
    """
    Defines the routing key based on the key format and values
    
    @param values: Contains the input values for the key
    @type values: c{dictionary} 
        
    @return: The generated routing key as a string
    @rtype: c{string}
    """
    _remove_extra_values(values)


    routing_key = ""
    for key in self.key_format:
        if key in values.keys():
            routing_key = routing_key+"."+values[key]
        else:
            routing_key = routing_key+".dontcare"
        
    return routing_key.lstrip(".") # Remove the first dot
       


def _remove_extra_values(values):
    """
    Checks for extra values in the value dictionary. Removes extra
    values and Prints a warning message to log if extra values are found
    """
    for key in values.keys():
        if key not in self.key_format:
            LOGGER.warning('Ignoring unsupported device property "%s"' % key)
            del values[key]
                
            
        
        

        

            

def get_queues(device_properties):
    """
    Returns a list of queues the worker should consume from based on device
    properties

    @param device_properties: The Device properties of the worker
    @type device_properties: c{dictionary}

        
    @rtype: C{list} 
    @return: A list of queues the worker should consume from
    """
    queues = []
    queues.append(device_properties["devicegroup"])
    if "devicename" in device_properties.keys():
        queues.append(device_properties["devicegroup"]+\
                      "."+device_properties["devicename"])
        if "deviceid" in device_properties.keys():
            queues.append(device_properties["devicegroup"]+\
                          "."+device_properties["devicename"]+\
                          "."+device_properties["deviceid"])

    # Reverse queues to give "more specific queues" higher priority
    queues.reverse()
        
    return queues
    
