from collections import defaultdict
from ots.common.api import TestedPackages

class PackageCollection(object):
    
    def __init__(self):
        self._tested_packages = {}
    
    def add_packages(self, environment, packages):
        if self._tested_packages.has_key(environment):
            tested_package = self._tested_packages[environment]
            tested_package.extend(packages)
        else:
            self._tested_packages[environment] = \ 
                                TestedPackages(environment, packages)

    def __iter__(self):
        for pkg in self._tested_packages.values():
            yield pkg 
