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

<<<<<<< HEAD
# First one is mandatory, others optional
VALID_PROPERTIES = ("devicegroup", "devicename", "deviceid")
                
def get_routing_key(device_properties):
    """
    Defines the routing key based on the key format and device_properties
    
    @param device_properties: Contains the input device_properties for the key
    @type device_properties: c{dictionary} 
=======
                
def get_routing_key(values):
    """
    Defines the routing key based on the key format and values
    
    @param values: Contains the input values for the key
    @type values: c{dictionary} 
>>>>>>> c15f38f... Moved get_queues() to ots.common.routing so that all routing key related code is in one place
        
    @return: The generated routing key as a string
    @rtype: c{string}
    """
<<<<<<< HEAD
    
    _check_input(device_properties)
=======
    _remove_extra_values(values)
>>>>>>> c15f38f... Moved get_queues() to ots.common.routing so that all routing key related code is in one place

    routing_key = ""
    for key in VALID_PROPERTIES:
        if key in device_properties.keys():
            routing_key = routing_key+"."+device_properties[key]
    return routing_key.lstrip(".") # Remove the first dot

<<<<<<< HEAD

def _check_input(device_properties):
    """
    Checks for extra values in the value dictionary. Prints a warning message to log if
    extra values are found
    """
    if not VALID_PROPERTIES[0] in device_properties.keys():
        raise Exception("Mandatory device property '%s' missing "% VALID_PROPERTIES[0])

    if VALID_PROPERTIES[1] not in device_properties and\
           VALID_PROPERTIES[2] in device_properties:
        raise Exception("Device property '%s' needs to be defined if '%s' is defined"% \
                        (VALID_PROPERTIES[1], VALID_PROPERTIES[2]))


    for key in device_properties.keys():
        if key not in VALID_PROPERTIES:
            LOGGER.warning('Ignoring unsupported device property "%s"' % key)
            del device_properties[key]

=======
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
>>>>>>> c15f38f... Moved get_queues() to ots.common.routing so that all routing key related code is in one place
                
def get_queues(device_properties):
    """
    Returns a list of queues the worker should consume from based on device
    properties

    @param device_properties: The Device properties of the worker
    @type device_properties: c{dictionary}

        
    @rtype: C{list} 
    @return: A list of queues the worker should consume from
    """
    _check_input(device_properties)
    queues = []
    queues.append(device_properties[VALID_PROPERTIES[0]])
    if VALID_PROPERTIES[1] in device_properties.keys():
        queues.append(device_properties[VALID_PROPERTIES[0]]+\
                      "."+device_properties[VALID_PROPERTIES[1]])
        if VALID_PROPERTIES[2] in device_properties.keys():
            queues.append(device_properties[VALID_PROPERTIES[0]]+\
                          "."+device_properties[VALID_PROPERTIES[1]]+\
                          "."+device_properties[VALID_PROPERTIES[2]])

<<<<<<< HEAD
=======
            

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

>>>>>>> c15f38f... Moved get_queues() to ots.common.routing so that all routing key related code is in one place
    # Reverse queues to give "more specific queues" higher priority
    queues.reverse()
        
    return queues
    
