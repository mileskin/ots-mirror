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
import time
import multiprocessing

import ots.worker
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
    worker.start()
    print "Starting Worker..."


class WorkerProcesses(object):
    """
    Utility class to allow a number of Workers to be launched
    """

    def __init__(self):
        """
        Create a number of Workers in a separate process
        """
        self._processes = []

    def start(self, no_of_workers = 1):
        """
        Start the processes

        @type no_of_processes : C{int}
        @param no_of_processes : The number of Workers
        """
        for proc in range(no_of_workers):
            worker_config_filename = self._worker_config_filename()
            worker_process = multiprocessing.Process(
                                         target = start_worker,
                                         args=(worker_config_filename,))
            worker_process.start()
            self._processes.append(worker_process)
            print "Starting Worker..."
        time.sleep(2)
 
    def terminate(self):
        """
        Terminate all the Workers
        """
        for proc in self._processes:
            print "Killing Worker..."
            proc.terminate()
        time.sleep(2)

    @staticmethod
    def _worker_config_filename():
        module = os.path.dirname(os.path.abspath(ots.worker.__file__))
        worker_config_filename = os.path.join(module, "config.ini")
        if not os.path.exists(worker_config_filename):
            raise Exception("%s not found"%(worker_config_filename))
        return worker_config_filename
