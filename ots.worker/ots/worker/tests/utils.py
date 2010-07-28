# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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

import logging

import subprocess
from subprocess import Popen, PIPE
import re

from ots.worker.server import Server
from ots.worker.client import Client
from ots.worker.connection import Connection


log = logging.getLogger(__name__)

def queue_size(connection ,queue):
    """
    Gets the number of messages in the queue
    """
    def _avoid_repeat():
        command = r"/usr/bin/env sudo /usr/sbin/rabbitmqctl list_queues | awk '/^test\t/ {print $2}'"
        p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
        log.debug("running q(%s)" % (command))
        (count,err) = p.communicate()
        count = int(count)
        log.debug("error output: " + str(err))
        return count
    try:
        return _avoid_repeat()
    except:
        # If these fail, no idea what's going on, let upper code catch it
        connection.connect()
        return _avoid_repeat()


class Utils(object):
    
    _connection = None
    
    def __init__(self,**kwargs):
        self.set_kwargs(**kwargs)
        self.client = None

    def set_kwargs(self,**kwargs):
        for (k,w) in kwargs.items():
            self.__dict__[k] = w
    
    def lazy_set(self):
        args = {
            'username':'guest',
            'password':'guest',
            'host':'localhost',
            'port':5672,
            'vhost':'/',
            'queue':'test',
            'routing_key':'test',
            'services_exchange':'test',
            'log_filename':None,
        }
        self.set_kwargs(**args)

    def spawn_connection(self, **extra_args):
        if not self._connection:
            args = dict(
                username = self.username,
                password = self.password,
                host = self.host,
                port = self.port,
                vhost = self.vhost,
                queue = self.queue,
                routing_key = self.routing_key,
                services_exchange = self.services_exchange,
            )
            for (k, v) in extra_args.items():
                args[k] = v
            self._connection = Connection(**args)
            self._connection.connect()
        return self._connection


    def spawn_client(self, **extra_args):
        if not self.client:
            args = dict(
                connection = self.spawn_connection()
            )
            for (k, v) in extra_args.items():
                args[k] = v
            self.client = Client(**args)
        return self.client

    def spawn_server(self,client=None,**extra_args):
        if not client:
            client=self.spawn_client()
        args = dict(
            log_filename = self.log_filename,
            client = client,
            connection = self.spawn_connection(),
        )
        for (k, v) in extra_args.items():
            args[k] = v
        server = Server(**args)
        return server

    def config(self,name):
        return getattr(self,name,'')

    def stop_rabbitmq(self):
        p = Popen("sudo /etc/init.d/rabbitmq-server stop", shell=True)
        exit_status = p.wait()
        return not bool(exit_status)

    def start_rabbitmq(self):
        p = Popen("sudo /etc/init.d/rabbitmq-server start", shell=True)
        exit_status = p.wait()
        return not bool(exit_status)
