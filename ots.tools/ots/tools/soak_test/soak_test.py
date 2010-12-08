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
Script to allow multiple calls to OTS runs 
through the XML rpc interface.

Hack script that could do with at bit of TLC

Be careful you could overload OTS with this script! 

To get a general feel of what is happening use the "dummy" option
in the config file before running on your OTS installation.

e.g.
python soak_test.py -t 10 -n 5 -c soak_test.cfg

"""

import sys
import random
import time
import xmlrpclib
import ConfigParser
import logging
from optparse import OptionParser

from twisted.internet import reactor
from twisted.internet import defer, threads

logger = logging.getLogger(__name__)

OPTIONS = "OPTIONS"
MODE = "MODE"
    

##########################################
# OTS RPC call
##########################################

def ots_xml_rpc(config_file, run_no):
    """
    Adaptation layer 
    - strips the parameter out of the config
    - chooses a random device
    """
    config = ConfigParser.ConfigParser()
    config.read("./soak_test.cfg")
    #
    sw_product = config.get(OPTIONS, "sw_product")
    build_id = "%s_%s"%(config.get(OPTIONS, "build_id"), run_no)
    email = config.get(OPTIONS, "email")
    email = [email.strip() for email in email.split(",")]    
    server = config.get(OPTIONS, "server")
    #
    options_dict = dict()
    image = config.get(OPTIONS, "image")
    options_dict['image'] = image
    #Get a random device
    devices = config.get(OPTIONS, "devices").split(",")
    idx = random.randrange(0, len(devices) , 1)
    device = devices[idx]
    logger.info("device: %s"%(device))     
    options_dict['device'] = "devicegroup:%s"%(device)
    #
    return _ots_xml_rpc(sw_product,
                        build_id, 
                        email,
                        options_dict,
		        server) 

def _ots_xml_rpc(sw_product, build_id, email, options_dict, server):
    """
    Runs a ots_xml_rpc call.
    A blocking operation
    """
    logger.info("calling OTS with params %s, %s %s, %s"%(sw_product, 
                                                         build_id, 
                                                         email, 
                                                         options_dict))

    if server:
        ots_interface = xmlrpclib.Server(server) 
        return ots_interface.request_sync(sw_product, 
                                          str(build_id), 
                                          email, 
                                          options_dict)

##########################################
# Remote Call Factory
##########################################

class RemoteCallFactory(object):
    """    
    Callable that can either be a `ots_trigger` or `dummy`
    
    - ots_trigger is makes an OTS RPC call
    - dummy is a stub for demo purposes
    """

    def __init__(self, config_file):
        self._config_file = config_file
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.dummy_run = bool(int(config.get(MODE, "dummy")))
            
    def ots_trigger(self, run_no):
        """
        Testrun with routing key based on random choice
        of devices
        """
        logger.info("Started run no: %s"%(run_no))
        return run_no, ots_xml_rpc(self._config_file, run_no)
 
    def dummy(self, run_no):
        """
        demo the harness code without kicking off runs
        """
        logger.info("Started run no: %s"%(run_no))
        def _dummy(config_file):
            print "in _dummy", run_no
            time.sleep(3)
        return run_no, _dummy(run_no)

    def __call__(self, run_no):
        """
        Callable to be run in reactor
        switches between a dummy run 
        and an ots trigger depending on config
        """
        if self.dummy_run:
            return self.dummy(run_no)
        return self.ots_trigger(run_no)


########################################
# RandomCallLaterGenerator
########################################

class RandomCallLaterGenerator(object):
    """
    Make multiple calls to a callable at random time intervals
    and stop the reactor when all the completed jobs have finished 
    """

    total_no_of_runs = 0
    no_of_completed_runs = 0

    def _run_in_thread(self, fn, *args):
        """
        Run fn in a thread and add the finishedHandler
        """
        d = threads.deferToThread(fn, *args)
        d.addCallback(self._finishedHandler)

    def _delayed_blocking_function(self, delay, fn, *args):
        """
        Call a blocking function after a delay
        """
        logger.info("initialising run at t=%s with args: %s"%(delay, args))
        reactor.callLater(delay, 
                          self._run_in_thread, 
                          fn, 
                          *args)

    def _finishedHandler(self, tuple):
        """
        Stops the reactor when all runs have finished

        tuple is a two element tuple (run_no, success)
        """
        run_no, success = tuple
        logger.info("Finished run: %s. Result: %s"%(run_no, success))
        self.no_of_completed_runs += 1
        if self.no_of_completed_runs == self.total_no_of_runs:
            logger.info("Success. Completed %s runs."%(self.total_no_of_runs))
            reactor.stop()
    
    def trigger_random_delayed_function(self, 
                                        no_of_runs, 
                                        start_time, 
                                        end_time, 
                                        remote_call_factory):
        """
        Repeatedly call `fn` in a thread `no_of_runs` times.
        The function is called after a random time delay 
        in the time range: start_time < t < end_time
        """
        #Start one immediately
        self._delayed_blocking_function(start_time, remote_call_factory, 0)
        #Randomly generate the rest
        for idx in range(no_of_runs - 1):
            t = random.randrange(start_time, end_time , 1)
            run_no = idx + 1
            self._delayed_blocking_function(t, remote_call_factory, run_no) 
        self.total_no_of_runs += no_of_runs

###################################################
# Main 
###################################################

def _init_logging():
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

def main(timespan, no_of_runs, ots_config):
    """
    Fire a number of test runs to OTS at 
    random time intervals
    """
    if True:
        #This has `undefined behaviour`. But is convenient :-) 
        print "Restoring SIGINT handler"
        import signal
        signal.signal(signal.SIGINT, signal.default_int_handler)
    #
    _init_logging()
    #
    config = ConfigParser.ConfigParser()
    config.read("./soak_test.cfg")
    #
    factory = RemoteCallFactory(ots_config)
    logger.info("Kicking off %s runs in timespan %s, using config %s"%(no_of_runs,
                                                                 timespan,
                                                                 ots_config)) 
    gen = RandomCallLaterGenerator()
    gen.trigger_random_delayed_function(no_of_runs, 0, timespan, factory)
    reactor.run()

####################################

if __name__ == "__main__":
    usage = "\n\nFires `n` xml_rpc requests\n"\
            "for the `image` specified in the config\n"\
            "on a random device taken from the `devices` in the config\n"\
            "at random intervals in the given time period `t`.\n\n"\
            "LEAVE RUNNING!\n"\
            "Finished runs are reported as they come back\n"\
            "and there is notification on receipt of all the runs.\n\n"\
            "WARNING: This script can overload OTS..\n"\
            "So set an appropriate timespan.\n\n"\
            "Example usage: %prog [options]\n"\
            "For debug/testing set device=dummy in the config file" 

    
    parser = OptionParser(usage = usage)
    #
    parser.add_option("-t", "--timespan",
                      help= "the duration of the test")
    #
    parser.add_option("-n", "--no_of_runs",
                      help = "the number of runs")
    #
    parser.add_option("-c", "--ots_config",
                      default = "./soak_test.cfg",
                      help = "the ots options config file")

    options, args = parser.parse_args()
    #
    if options.timespan is None or options.no_of_runs is None:
        parser.print_help()
        sys.exit()
    
    main(int(options.timespan), 
         int(options.no_of_runs), 
         options.ots_config)
