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
import logging

from ots.server.server_config_filename import server_config_filename

from ots.server.hub.options import Options 
from ots.server.hub.sandbox import sandbox

"""
Safely create the Options API from a dictionary 
setting configurable defaults
""" 

LOG = logging.getLogger(__name__)

###################################
# DEFAULTS 
###################################

CONFIG_FILE_OPTIONS_DICT = {}


###############################
# OPTIONS FACTORY 
###############################

class OptionsFactory(object):
    """
    Factory for Options

    Essentially this is an Adaptation layer.
    
    It merges two input dictionaries:
    
        - The `options_dict` on the interface
        - The config options arising from the sw_pdt selection


    The output are "Core" and "Extended" Options.
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
            pdts = configobj.ConfigObj(conf).get('swproducts').keys()
            msg = "'%s' not found in sw products: %s"%(sw_product, pdts)
            raise ValueError(msg)
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
    @sandbox(CONFIG_FILE_OPTIONS_DICT)
    def config_file_options_dict(self):
        """
        The options coming from the config file relating to 
        the sw product

        rtype : C{dict}
        rparam : The Options from the config file
        """
        #Get the default options for the sw product from conf file
        defaults = self._default_options_dict(self._sw_product)
        return self._sanitise_options(defaults)
       
    @property 
    def extended_options_dict(self):
        """
        Extended options are key, value pairs that 
        are not recognised as the core Option attributes

        rtype : C{dict}
        rparam : Additional Options passed to OTS  
        """
        sanitised_options_dict = self._sanitise_options(self._options_dict)
        config_file_options_dict = self.config_file_options_dict

        #Throw out the core options
        for key in self.core_options_names:
            if sanitised_options_dict.has_key(key):
                sanitised_options_dict.pop(key)
            if config_file_options_dict.has_key(key):
                config_file_options_dict.pop(key)    
        
        config_file_options_dict.update(sanitised_options_dict)
        return config_file_options_dict
        
    @property 
    def core_options_dict(self):
        """
        Take only the recognised core options 
        Overrides the defaults depending on configuration
        
        rtype : C{dict}
        rparam : The treated Options dictionary
        """
        #Take only the core options
        core_options_dict = {}
        core_config_file_options_dict = {}
        for key in  self.core_options_names:
            if key in self._options_dict:
                core_options_dict[key] = self._options_dict[key]
            if key in self.config_file_options_dict:
                core_config_file_options_dict[key] = \
                     self.config_file_options_dict[key]
        
        core_options_dict.update(core_config_file_options_dict)
  
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
            raise ValueError("Missing `image` parameter")
        LOG.debug("Calling options with kwarg: %s"%(self.core_options_dict))
        return Options(**self.core_options_dict)
