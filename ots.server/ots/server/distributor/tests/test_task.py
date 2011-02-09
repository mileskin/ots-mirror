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

import unittest

from ots.server.distributor.task import Task, TaskException
from ots.common.dto.api import TaskCondition

class TestTask(unittest.TestCase):

    def test_transition(self):
        task = Task([1], 0)
        self.assertEquals(task._WAITING, task.current_state)
        task.transition(TaskCondition.START)
        self.assertEquals(task._STARTED, task.current_state)
        task.transition(TaskCondition.FINISH)
        self.assertEquals(task._FINISHED, task.current_state)
        self.assertRaises(TaskException, task.transition, "foo")
        self.assertRaises(TaskException, task.transition, TaskCondition.START)
    
    def test_is_finished(self):
        task = Task([1], 0)
        self.assertFalse(task.is_finished)
        task.current_state = task._FINISHED
        self.assertTrue(task.is_finished)
        
if __name__ == "__main__":
    unittest.main()
