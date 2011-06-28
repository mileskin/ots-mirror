# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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


#!/usr/bin/env python
"""A command line tool for triggering a test run via OTS XML-RPC interface"""

from optparse import OptionParser, OptionGroup
import configobj
import logging
import xmlrpclib
import sys
import os


def read_test_plan(filepath):
    """
    Reads given test plan and returns the file data.
    """
    testplan_data = None
    if os.path.exists(filepath):
        testplan_fb = open(filepath, 'r')
        testplan_data = testplan_fb.read(-1)
        testplan_fb.close()

    return testplan_data

def _parse_configuration_file(configfile, section):
    """
    Read settings from the configuration file
    
    @type configfile: C{str}
    @param configfile: Path to the configuration file

    @type section: C{str}
    @param section: Subsection in the configuration file
    
    @rtype: C{dict}
    @return: Dictionary of settings
    
    """
    
    if not os.path.exists(configfile):
        print "Error: Configuration file doesn't exists!"
        print "File path %s" % configfile
        sys.exit(-1)
    config = configobj.ConfigObj(configfile)
    
    default_settings = {}
    
    for (name, value) in config.items():
        if type(value) is configobj.Section:
            continue
        default_settings[name] = value
    
    if section:
        section_settings = config.get(section)
        if section_settings is None:
            print "Error: Subsection not found: %s" % section
            sys.exit(-1)
        
        default_settings.update(section_settings)
    
    return default_settings

def _parameter_validator(config_options, cmdline_options):
    """
    Compines configuration options with command line options and removes
    extra options.
    
    @type config_options: C{dict}
    @param config_options: Path to the configuration file

    @type cmdline_options: C{dict}
    @param cmdline_options: Subsection in the configuration file
    
    @rtype: C{dict}
    @return: Dictionary of settings
    
    """
    
    del cmdline_options["configfile"]
    del cmdline_options["configsection"]
    
    for (name, value) in cmdline_options.items():
               
        # Skit not set values
        if value is not None and value is not "" and value is not 0:
            if name == "options":
                try:
                    for option in value.split(" "):
                        key, value = option.split(":")
                        config_options[key] = value
                except AttributeError:
                    pass
            # Extend email list
            elif name == "email":
                email_list = config_options.get(name, None)
                cmd_list = value.split(',')
                # Config file includes a list
                if type(email_list) is list:
                    email_list.extend(cmd_list)
                # Ccnfig file includes only string
                elif type(email_list) is str:
                    email_list = [email_list]
                    email_list.extend(cmd_list)
                # No email definition in configuration file
                else:
                    config_options[name] = cmd_list
            else:
                config_options[name] = value
    
    return config_options

def ots_trigger(options):
    """
    Executes ots testrun over xml-rpc.
    """
    build_id = options.get('build_id')
    sw_product = options.get('sw_product')
    email_list = options.get('email')
    server = options.get('server')
    
    # Not needed anymore
    del options['build_id']
    del options['sw_product']
    del options['email']
    del options['server']

    if options.get('hw_testplans'):
        testplans = list()
        for testplan in options.get('hw_testplans'):
            testplan_data = read_test_plan(testplan)
            testplans.append((os.path.basename(testplan), testplan_data))
        ots_options['hw_testplans'] = testplans
    if options.get('host_testplans'):
        testplans = list()
        for testplan in options.get('host_testplans'):
            testplan_data = read_test_plan(testplan)
            testplans.append((os.path.basename(testplan), testplan_data))
        options['host_testplans'] = testplans

    ots_interface = xmlrpclib.Server("http://%s/" % server)
    
    return ots_interface.request_sync(sw_product,
                                      build_id,
                                      email_list,
                                      options)


def parse_commandline_arguments():
    """
    Parses command line parameters. Makes sure that enough parameters are given.

    Returns OptionParser options object.
    """

    usage = "usage: %prog [options] \n" + \
            "example: " + \
            "%prog -i image_url"
                
    parser = OptionParser(usage=usage)
    
    mandatory_group = OptionGroup(parser, "Mandatory parameters")
    
    mandatory_group.add_option("-s", "--server", dest="server", action="store",
                               type="string", help="OTS server URL (mandatory)",
                               metavar="SERVER")

    mandatory_group.add_option("-b", "--build_id", dest="build_id", action="store",
                               type="string", help="build request ID (mandatory)",
                               metavar="ID")

    mandatory_group.add_option("-i", "--image", dest="image", action="store",
                               type="string", help="URL to image file (mandatory)",
                               metavar="IMAGE", default="")

    mandatory_group.add_option("-p", "--sw_product", dest="sw_product", action="store",
                               type="string",
                               help="software product (mandatory)",
                               metavar="SWPRODUCT")

    mandatory_group.add_option("-e", "--email", dest="email", action="store",
                               type="string",
                               help="email addresses as a comma separated " \
                               "list (mandatory)",
                               metavar="EMAIL", default="")
    
    parser.add_option_group(mandatory_group)
    
    optional_group = OptionGroup(parser, "Optional parameters")

    optional_group.add_option("-d", "--device", dest="device", action="store",
                              type="string", help="device properties", metavar="DEVICE",
                              default="")

    optional_group.add_option("-t", "--testpackages", dest="testpackages",
                              action="store", type="string",
                              help="list of test packages separated with comma",
                              metavar="TESTPACKAGES", default="")

    optional_group.add_option("-o", "--hostpackages", dest="hosttest", action="store",
                              type="string",
                              help="list of host test packages separated with space",
                              metavar="HOSTTEST", default="")

    optional_group.add_option("-C", "--chrootpackages", dest="chroottest",
                              action="store", type="string",
                              help="list of test packages separated with space",
                              metavar="CHROOTTEST", default="")

    optional_group.add_option("-m", "--timeout", dest="timeout", action="store",
                              type="int", help="global timeout (minutes)",
                              metavar="TIMEOUT", default=0)

    optional_group.add_option("-f", "--filter", dest="testfilter", action="store",
                              type="string", help="test filter string",
                              metavar="FILTER", default="")

    optional_group.add_option("-n", "--input_plugin", dest="input_plugin",
                              action="store",
                              type="string", help="input plugin to use",
                              metavar="PLUGIN", default="")

    optional_group.add_option("-c", "--distribution",
                              dest="distribution_model",
                              action="store",
                              type="string",
                              help="task distribution model (for example 'perpackage')",
                              metavar="DISTMODEL")

    optional_group.add_option("-r", "--rootstrap",
                              dest="rootstrap",
                              action="store",
                              type="string",
                              help="URL to rootstrap file",
                              metavar="ROOTSTRAP")

    optional_group.add_option("-T", "--deviceplan",
                              dest="hw_testplans",
                              action="append",
                              type="string",
                              help="test plan for device based execution",
                              metavar="FILE")
    
    optional_group.add_option("-O", "--hostplan",
                              dest="host_testplans",
                              action="append",
                              type="string",
                              help="test plan for host based execution",
                              metavar="FILE")

    optional_group.add_option("-S", "--libssh2",
                              dest="use_libssh2",
                              action="store_true",
                              help="use testrunner-lite libssh2 support",
                              default=False,
                              metavar="BOOL")

    optional_group.add_option("-x", "--options",
                              dest="options",
                              action="store",
                              type="string",
                              help="options in form 'key:value key:value'",
                              metavar="OPTIONS")
    
    parser.add_option_group(optional_group)

    config_group = OptionGroup(parser, "Configuration file options")
    config_group.add_option("", "--config",
                            dest="configfile",
                            action="store",
                            type="string",
                            help="Configuration file for default settings, default empty",
                            metavar="FILE")
    config_group.add_option("", "--section",
                            dest="configsection",
                            action="store",
                            type="string",
                            help="Subsection in the configuration file, default empty")
    
    parser.add_option_group(config_group)

    # parser returns options and args even though we only need options
    # Disabling pylint complain about unused variable
    # pylint: disable=W0612
    (options, args) = parser.parse_args()
    
    config_options = {}
    if options.configfile:
        config_options = _parse_configuration_file(options.configfile, options.configsection)
    
    # Checks all parameters and removes extra parameters
    parameters = _parameter_validator(config_options, options.__dict__)
    
    if  not (parameters.get('server') and \
             parameters.get('build_id') and \
             parameters.get('sw_product') and \
             parameters.get('email') and \
             parameters.get('image')):
        print "\nError: Some of mandatory parameters were missing!"
        print "See --help"
        sys.exit(-1)
    elif not bool(parameters.get('rootstrap')) == bool(parameters.get('chroottest')):
        print "\nError: Both rootstrap and chrootpackages needs to be defined" \
            " if using one of them."
        print "See --help"
        sys.exit(-1)

    return parameters


def main():
    """Main function"""
    options = parse_commandline_arguments()

    log_format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        stream=sys.stdout)

    log = logging.getLogger(__name__)
    log.info("Calling OTS XML-RPC with options:\n %s" % str(options))
    result = ots_trigger(options)
    log.info("Result: %s" % result)


if __name__ == '__main__':
    main()

