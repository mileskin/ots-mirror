
class PackageResults(object):
    """
    Container for the Package results
    """

    def __init__(self, 
                 testpackage, 
                 environment):
        self.testpackage = testpackage
        self.environment = environment
        self.significant_results = []
        self.insignificant_results = []

