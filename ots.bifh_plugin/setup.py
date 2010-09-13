from setuptools import setup, find_packages

setup(
      name = "ots.bifh_plugin",
      namespace_packages = ["ots", "ots.bifh_plugin"],
      version =  0.8,
      include_package_data = True,
      packages = find_packages(),
      entry_points={"BifhPlugin":
                ["ots.bifh_plugin.bifh_plugin = ots.bifh_plugin.bifh_plugin"]},
     )
