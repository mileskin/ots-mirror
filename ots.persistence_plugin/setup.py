from setuptools import setup, find_packages

setup(
      name = "ots.persistence_plugin",
      namespace_packages = ["ots", "ots.persistence_plugin"],
      version =  0.8,
      include_package_data = True,
      packages = find_packages(),
      entry_points={"PersistencePlugin":
            ["ots.persistence_plugin.persistence_plugin "\
             "= ots.persistence_plugin.persistence_plugin"]},
     )
