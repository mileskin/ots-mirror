import warnings
warnings.filterwarnings("ignore", "Module (.*) was already imported (.*)")

__import__('pkg_resources').declare_namespace(__name__)

