import unittest

from ots.common.api import TestedPackages

from ots.results.environment_packages import PackageCollection

class TestEnvironmentCollection(unittest.TestCase):

    def test_add_package(self):
        coll = PackageCollection()
        print dir(coll)
        coll[1] = 22


        


if __name__ == "__main__":
    unittest.main()
