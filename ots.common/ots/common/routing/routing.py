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

from copy import deepcopy, copy

class Routing(object):
    """
    This class can be used for defining the routing keys and queue names in AMQP
    """
    
    def __init__(self, key_format):
        """
        @param key_format: A list that defines the format of the routing key
        @type key_format: A list of c{string}   
        """
        self.key_format = key_format
                
    def get_routing_key(self, values):
        """
        Defines the routing key based on the key format and values
        
        @param values: Contains the input values for the key
        @type values: c{dictionary} 
        
        @return: The generated routing key as a string
        @rtype: c{string}
        """
        self._remove_extra_values(values)


        routing_key = ""
        for key in self.key_format:
            if key in values.keys():
                routing_key = routing_key+"."+values[key]
            else:
                routing_key = routing_key+".dontcare"
        
        return routing_key.lstrip(".") # Remove the first dot
       
        
    def get_list_of_queues(self, values):
        """
        Defines all the queues a worker should connect.
        
        @param values: The property values of the worker
        @type values: c{dictionary}
        
        @return: A list of queue names.
        @rtype: c{list} containing c{string}s.
        """
        queues = []
        
        queue_properties = [{}] # all the value combinations as dictionaries
        
        for key in self.key_format:
            temp =  copy(queue_properties)
            for queue in queue_properties:
                new_queue = deepcopy(queue)
                new_queue[key] = values[key]
                temp.append(new_queue)
            queue_properties = temp

        # Generate queue strings
        for properties in queue_properties:
            queue = self.get_routing_key(properties)
            queues.append(queue)
        return queues




    def _remove_extra_values(self, values):
        """
        Checks for extra values in the value dictionary. Removes extra
        values and Prints a warning message to log if extra values are found
        """
        for key in values.keys():
            if key not in self.key_format:
                #self.log.warning('Ignoring value "%s" because it is not in key format.' % key)
                del values[key]
                
            
        
        

        

            
