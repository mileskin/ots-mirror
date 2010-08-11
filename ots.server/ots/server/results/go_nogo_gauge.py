from ots.server.results.testrun_result import TestrunResult

class PackageException(Exception):
    pass


def _required_packages(all_executed, packages, host_packages, hw_enabled):
     """
     Generates a list of test packages defined in testrun.

     Returns:
         A list of tuples in form testpackage,environment.
     """

     def host_tests_found(pkgs):
         """Return True if pkgs dict has at least one key for a host test"""
         return any([key for key in pkgs.keys() if re.match("host.*", key)])

     all_packages = []

     #Executed packages per environment are the required packages
     for environment in executed.keys():
         for package in executed[environment]:
             all_packages.append((package, environment.lower()))

     if not host_tests_found(executed) and host_packages and hw_enabled:
         for package in host_packages:
             all_packages.append(package+"-host_hardware")

     if not 'hardware' in executed.keys() and packages and hw_enabled:
         for package in packages:
             all_packages.append(package+"-hardware")

     return all_packages

def _check_run_validity(all_executed, packages, host_packages, hw_enabled):
    required_packages = _required_packages(all_executed, 
                                           packages, 
                                           host_packages, 
                                           hw_enabled)

    if not required_packages:
        raise PackageException("No test packages defined nor found.")
    missing = False  #FIXME set difference here
    if missing: 
        missing = ", ".join(missing)
        raise PackageException("Missing from: %s"%(missing)) 


def _reduce_package_results(package_results_list):
    ret_val = TestResult.NO_CASES
    self._check_run_validity() 
    results = []
    for package_results in package_results_list:
        results.extend(package.significant_results)
        if self.insignificant_tests_matter:
            results.extend(package.insignificant_results)
    if results:
        if results.count(TestrunResult.PASS) == len(results):
            ret_val = TestrunResult.PASS
        else:
            ret_val = TestrunResult.FAIL
    return ret_val


def go_nogo_gauge(all_executed, 
                  packages, 
                  host_packages, 
                  hw_enabled,
                  package_results_list):
    _check_run_validity(all_executed, packages, host_packages, hw_enabled)
    return _reduce_package_results(package_results_list)
