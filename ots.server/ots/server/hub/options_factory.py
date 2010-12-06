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

# 02110-1301 USA
# ***** END LICENCE BLOCK *****

import os
import configobj
from ots.server.server_config_filename import server_config_filename
from ots.server.hub.options import Options 

"""
Safely create the Options API from a dictionary 
setting configurable defaults
""" 

class OptionsFactoryException(Exception):
    pass

###############################
# OPTIONS FACTORY 
###############################

class OptionsFactory(object):
    """
    Factory for Options

    Preprocesses the options dictionary 
    Sorts the Options into Core and Extended Options
    """

    aliases = {"image" : "image_url",
               "emmc" : "emmc_flash_parameter",
               "flasher" : "flasherurl",
               "packages" : "test_packages"}

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
    def _sanitise_options(options_dict):
        """
        sanitises the options dict (hyphens aren't Python friendly)

        @type options_dict : C{dict} or None
        @param options_dict : The dictionary of options

        @rtype: C{dict} or None
        @returns: The dictionary of options with "-" replaced by "_"
        """
        return dict([(k.replace("-","_"), v) for k,v in options_dict.items()])
                    
    @staticmethod
    def _default_options_dict(sw_product):
        """
        @type sw_product : C{str}
        @param sw_product : The name of the software product

        @rtype default_options_dict : C{dict} or None
        @param default_options_dict : The dictionary of options

        Get the default options for the SW product
        """
        conf = server_config_filename()
        config = configobj.ConfigObj(conf).get('swproducts').get(sw_product)
        if not config:
            raise OptionsFactoryException("Unknown SW Product")
        return config

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
        
        names = Options.__init__.im_func.func_code.co_varnames
        return names

    @property 
    def extended_options_dict(self):
        """
        key, value pairs that aren't recognised are assumed 
        to be part of the extended options

        rtype : C{dict}
        rparam : Additional Options passed to OTS  
        """
        #Get the default options for the sw product from conf file
        defaults = self._default_options_dict(self._sw_product)
        sanitised_options = self._sanitise_options(defaults)
        sanitised_options.update(self._sanitise_options(self._options_dict))
        extended_options_dict = sanitised_options

        for key in self.core_options_names:
            if extended_options_dict.has_key(key):
                extended_options_dict.pop(key)
        return extended_options_dict
        
    @property 
    def core_options_dict(self):
        """
        Adapts the options dictionary to the interface 
        Overrides the defaults depending on configuration
        and changes the names of the supported interface.
        
        rtype : C{dict}
        rparam : The treated Options dictionary
        """

        #Throw out the extended options
        core_options_dict = dict((key, self._options_dict[key]) 
                                 for key in  self.core_options_names 
                                 if key in self._options_dict)
        #Patch aliases 
        for new_name, old_name in self.aliases.items():
            if self._options_dict.has_key(old_name):
                core_options_dict[new_name] = self._options_dict[old_name]
        return core_options_dict

    #####################################
    # FACTORY METHOD
    #####################################

    def __call__(self):
        """
        rtype : C{ots.server.hub.options.Options
        rparam : The Options
        """
        if not self.core_options_dict.has_key("image"):
            raise OptionsFactoryException("Missing `image` parameter")
        return Options(**self.core_options_dict)
