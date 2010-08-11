import unittest

from ots.server.model.testrun import Testrun 
from ots.server.model.tests.system.mock_taskrunner import MockTaskRunner


class TestOTSModel(unittest.TestCase):

    def test_ots_model(self):
        mock_task_runner = MockTaskRunner()
        mock_task_runner.run()

if __name__ == "__main__":
    unittest.main()
