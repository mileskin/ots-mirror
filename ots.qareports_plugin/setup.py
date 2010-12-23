from setuptools import setup, find_packages

setup(
    name="ots.qareports_plugin",
    namespace_packages=["ots", "ots.qareports_plugin"],
    version=0.1,
    include_package_data=True,
    packages=find_packages(),
    install_requires=['ots.server'],
    entry_points={"ots.publisher_plugin":
          ["publisher_klass = "\
           "ots.qareports_plugin.qareports_plugin:QAReportsPlugin"]},
    data_files=[('/etc',
                 ['ots/ots_qareports_plugin/ots_qareports_plugin.conf'])]
    )
