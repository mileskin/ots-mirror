
#This shouldn't be necessary 
#http://bugs.python.org/setuptools/issue36

import warnings
warnings.filterwarnings("ignore", "Module (.*) was already imported (.*)")

__import__('pkg_resources').declare_namespace(__name__)

