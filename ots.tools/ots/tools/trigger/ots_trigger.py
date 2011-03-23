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
"""A command line tool for starting testruns with ots xmlrpc"""

from optparse import OptionParser
import logging
import xmlrpclib
import sys

def ots_trigger(options):
    """
    Executes ots testrun over xml-rpc.
    """
    build_id = options.id
    ots_options = dict()
    if options.device:
        ots_options['device'] = options.device
    sw_product = options.sw_product
    email_list = options.email.split(',')

    try:
        for option in options.options.split(" "):
            key, value = option.split(":")
            ots_options[key] = value
    except AttributeError:
        pass

    if options.image:
        ots_options['image'] = options.image
    if options.testpackages:
        ots_options['packages'] = options.testpackages
    if options.filter:
        ots_options['testfilter'] = options.filter
    if options.input_plugin:
        ots_options['input_plugin'] = options.input_plugin
    if options.hosttest:
        ots_options['hosttest'] = options.hosttest
    if options.timeout:
        ots_options['timeout'] = options.timeout
    if options.distribution:
        ots_options['distribution_model'] = options.distribution

    ots_interface = xmlrpclib.Server("http://%s/" % options.server)
    return ots_interface.request_sync(sw_product,
                                       build_id,
                                       email_list,
                                       ots_options)



def parse_commandline_arguments():
    """
    Parses command line parameters. Makes sure that enough parameters are given.

    Returns OptionParser options object.
    """

    usage = "usage: %prog [options] \n" + \
            "example: " + \
            "%prog -i image_url"
                
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--server", dest="server", action="store",
                      type="string", help="Ots server URL",
                      metavar="SERVER")

    parser.add_option("-b", "--build_id", dest="id", action="store",
                      type="string", help="Build request ID", metavar="ID")

    parser.add_option("-i", "--image", dest="image", action="store",
                      type="string", help="Url to image file", metavar="IMAGE",
                      default="")

    parser.add_option("-d", "--device", dest="device", action="store",
                      type="string", help="Device properties", metavar="DEVICE",
                      default="")

    parser.add_option("-p", "--sw_product", dest="sw_product", action="store",
                      type="string",
                      help="Sw product",
                      metavar="SWPRODUCT")

    parser.add_option("-e", "--email", dest="email", action="store",
                      type="string",
                      help="Email addresses as a comma separated list",
                      metavar="EMAIL", default="")

    parser.add_option("-t", "--testpackages", dest="testpackages",
                      action="store", type="string",
                      help="List of test packages separated with comma",
                      metavar="TESTPACKAGES", default="")


    parser.add_option("-m", "--timeout", dest="timeout", action="store",
                      type="int", help="Global timeout (minutes)",
                      metavar="TIMEOUT", default=0)


    parser.add_option("-o", "--hostpackages", dest="hosttest", action="store",
                      type="string",
                      help="List of host test packages separated with space",
                      metavar="HOSTTEST", default="")

    parser.add_option("-f", "--filter", dest="filter", action="store",
                      type="string", help="Test filter string",
                      metavar="FILTER", default="")

    parser.add_option("-n", "--input_plugin", dest="input_plugin",
                      action="store",
                      type="string", help="input_pluging to use",
                      metavar="PLUGIN", default="")

    parser.add_option("-c", "--distribution",
                      dest="distribution",
                      action="store",
                      type="string",
                      help="task distribution model(for example 'perpackage')",
                      metavar="DISTMODEL")

    parser.add_option("-x", "--options",
                      dest="options",
                      action="store",
                      type="string",
                      help="Options in form 'key:value key:value'",
                      metavar="OPTIONS")

    # parser returns options and args even though we only need options
    # Disabling pylint complain about unused variable
    # pylint: disable-msg=W0612
    (options, args) = parser.parse_args()
        
    
    if  not (options.server and options.id and options.sw_product and\
                 options.email and options.image):
        parser.print_help()
        sys.exit(-1)

    return options


def main():
    """Main function for running mother of all flashers from command line"""
    options = parse_commandline_arguments()

    log_format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        stream=sys.stdout)

    log = logging.getLogger(__name__)
    log.info("Calling ots xml-rpc with options:\n %s" % str(options))
    result = ots_trigger(options)
    log.info("Result: %s" % result)



if __name__ == '__main__':
    main()
