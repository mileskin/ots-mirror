
 def required_packages(testrun):
     """
     Generates a list of test packages defined in testrun.

     Returns:
         A list of tuples in form testpackage,environment.
     """

     def host_tests_found(pkgs):
         """Return True if pkgs dict has at least one key for a host test"""
         return any([key for key in pkgs.keys() if re.match("host.*", key)])

     all_packages = []
     executed = testrun.get_all_executed_packages() #provided by workers
     packages = testrun.get_testpackages() #user-defined. For HW and SB
     host_packages = testrun.get_host_testpackages() #user-defined. For Host
     hw_enabled = testrun.hardware_testing_enabled()


     #Executed packages per environment are the required packages
     for environment in executed.keys():
         for package in executed[environment]:
             all_packages.append((package, environment.lower()))

     #If executed list does not contain packages for all the environments
     #that were specified by user (bifh), append the package list with 
     #packages provided by user for that environment.
     #This can happen for example if a worker times out after image flashing
     #and if timeout is not detected and handled properly before this code
     #is executed.

     #Note: "host_scratchbox" is not checked below!

     if not host_tests_found(executed) and host_packages and hw_enabled:
         for package in host_packages:
             all_packages.append(package+"-host_hardware")

     if not 'hardware' in executed.keys() and packages and hw_enabled:
         for package in packages:
             all_packages.append(package+"-hardware")

     if not 'scratchbox' in executed.keys() and packages and sb_enabled:
         for package in packages:
             all_packages.append(package+"-scratchbox")
     return all_packages


