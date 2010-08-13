


class ExecutedPackage(object):
    """
    Container class for the Packages executed by the Testrun
    """

    HOST_TEST_PATTERN = "host.*"
    HARDWARE = "hardware"

    def __init__(self, environment, packages):
        self.environment = environment
        self.packages = packages

    @property    
    def is_host_test(self):
        return re.match(self.HOST_TEST_PATTERN, self.environment)

    @property 
    def is_hardware(self):
        return self.HARDWARE in self.environment

