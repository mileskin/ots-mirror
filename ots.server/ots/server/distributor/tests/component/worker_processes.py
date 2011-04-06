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

import os
import time
import multiprocessing
from multiprocessing import Pool

import ots.worker
from ots.worker.worker import create_amqp_log_handler
from ots.worker.api import worker_factory

def start_worker(config_filename):
    """
    Start the OTS Worker
    Helper for multiprocessing purposes
    """
    #Make sure ots_mock is on the PATH
    dirname = os.path.dirname(os.path.abspath(ots.worker.__file__))
    os.path.join(dirname, "tests")
    mock_dir = os.path.join(dirname, "tests")
    new_path =  os.environ["PATH"] + ":" + mock_dir
    os.environ["PATH"] = new_path
    #create and start it
    worker = worker_factory(config_filename)

#    AMQP log handler disabled because of problems in error situations
#    (See test_worker_alive_after_server_timeout in distributor component tests)
#    TODO: Fix in 0.9

#    amqp_log_handler = create_amqp_log_handler() 
#    worker.amqp_log_handler = amqp_log_handler 
    
    worker.start()

class WorkerProcesses(object):
    """
    Utility class to allow a number of Workers to be launched
    """

    def __init__(self):
        """
        Create a number of Workers in a separate process
        """
        self._processes = []

    def start(self, no_of_workers = 1, config_file=""):
        """
        Start the processes

        @type no_of_workers : C{int}
        @param no_of_workers : The number of Workers

        @rtype: C{list} of C{int}
        @returns: pids of the started processes
        """
        if config_file:
            worker_config_filename = config_file
        else:
            worker_config_filename = self._worker_config_filename()
        pids = []
        for proc in range(no_of_workers):
            worker_process = multiprocessing.Process(
                                         target = start_worker,
                                         args=(worker_config_filename,))
            worker_process.start()
            pids.append(worker_process.pid)
            self._processes.append(worker_process)           
        time.sleep(1)
        return pids
 
    def terminate(self):
        """
        Terminate all the Workers
        """
        for proc in self._processes:
            proc.terminate()
        time.sleep(2)
        self._processes = []

    @property    
    def exitcodes(self):
        return [proc.exitcode for proc in self._processes]

    @staticmethod
    def _worker_config_filename():
        module = os.path.dirname(os.path.abspath(ots.worker.__file__))
        worker_config_filename = os.path.join(module, "config.ini")
        if not os.path.exists(worker_config_filename):
            raise Exception("%s not found"%(worker_config_filename))
        return worker_config_filename
