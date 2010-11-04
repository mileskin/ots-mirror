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

###############################
# OPTIONS FACTORY 
###############################

class OptionsFactory(object):
    """
    Factory for Options

    Preprocesses the options dictionary 
    Sorts the Options into Core and Extended Options
    """

    def __init__(self, sw_product, options_dict):
        """
        @type sw_product : C{str}
        @param sw_product : The name of the software product

        @type options_dict : C{dict}
        @param options_dict: The dictionary of options
        """
        self._sw_product = sw_product
        self._options_dict = options_dict
    
    #####################################
    # HELPER 
    #####################################

    @staticmethod
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

    #######################################
    # PROPERTIES
    #######################################

    @property 
    def core_options_names(self):
        """
        The names of the Options necessary for core functionality  
        
        rtype : C{tuple} of C{str}
        rparam : The core function names 
        """
        
        return Options.__init__.im_func.func_code.co_varnames

    @property 
    def extended_options_dict(self):
        """
        key, value pairs that aren't recognised are assumed 
        to be part of the extended options

        rtype : C{dict}
        rparam : Additional Options passed to OTS  
        """
        extended_options_dict = self._options_dict.copy()
        for key in self.core_options_names:
            if extended_options_dict.has_key(key):
                extended_options_dict.pop(key)
        return extended_options_dict
        
    @property 
    def core_options_dict(self):
        """
        Adapts the options dictionary to the interface 
        Overrides the defaults depending on configuration
        
        rtype : C{dict}
        rparam : The treated Options dictionary
        """

        #Throw out the extended options
        core_options_dict = dict((key, self._options_dict[key]) 
                  for key in  self.core_options_names 
                          if key in self._options_dict)

        #sanitise the dict (hyphens aren't Python friendly)
        sanitised_options_dict = dict([(k.replace("-","_"), v) 
                                       for k,v in core_options_dict.items()])
        #Get the defaults for the sw product
        merged_options_dict = self._default_options_dict(self._sw_product)
        #
        merged_options_dict.update(sanitised_options_dict)

        return merged_options_dict

    #####################################
    # FACTORY METHOD
    #####################################

    def __call__(self):
        """
        rtype : C{ots.server.hub.options.Options
        rparam : The Options
        """
        return Options(**self.core_options_dict)
