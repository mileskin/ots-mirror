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

"""
This module contains components for defining routing keys

This implementation is in response to 
http://bugs.meego.com/show_bug.cgi?id=8024
i.e. the requirement to support a Directory Service based naming mechanism.

AMQP 0.8 does not lend that well to this kind of naming hence this module 
provides Adaptation methods and the rules to create routing_keys that 
use a  Name Spaced approach. 
"""

import logging
LOGGER = logging.getLogger(__name__)

import warnings
warnings.warn("AMQP 0.8 implementation.")


####################################
# RULES 
####################################

#The rules necessary to generatate routing keys
#from Namespaces from Dictionaries.

DEVICE_GROUP = "devicegroup"
DEVICE_NAME = "devicename"
DEVICE_ID = "deviceid"


# The Name Space ordering...
# First one is mandatory, others optional
# To be recognised the Keywords of the Dictionaries 
# must therefore match the VALID_PROPERTIES

VALID_PROPERTIES = (DEVICE_GROUP, DEVICE_NAME, DEVICE_ID)

######################################
                
def get_routing_key(device_properties):
    """
    Defines the routing key based on the key format and device_properties
    
    @param device_properties: Contains the input device_properties for the key
    @type device_properties: c{dictionary} 
        
    @return: The generated routing key as a string
    @rtype: c{string}
    """
    
    _check_input(device_properties)

    routing_key = ""
    for key in VALID_PROPERTIES:
        if key in device_properties.keys():
            routing_key = routing_key+"."+device_properties[key]
    return routing_key.lstrip(".") # Remove the first dot


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

                
def get_queues(device_properties):
    """
    Returns a list of queues the worker should consume from based on 
    Name Spaces. The Names Spaces are generated from the device
    properties and the ordering rules set out at the top of the file.  

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

    # Reverse queues to give "more specific queues" higher priority
    queues.reverse()
        
    return queues
    
