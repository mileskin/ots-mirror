
class Package(object):
    """
    Container for the Package results
    """

    def __init__(self, 
                 testpackage, 
                 environment,
                 insignificant_tests_matter):
        self.testpackage = testpackage
        self.environment = environment
        self.insignificant_tests_matter = insignificant_tests_matter
        self.significant_results = []
        self.insignificant_results = []

