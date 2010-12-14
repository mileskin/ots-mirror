from setuptools import setup, find_packages

setup(
	name="ots.logger_plugin",
	namespace_packages=["ots", "ots.logger_plugin"],
	version=0.1,
	include_package_data=True,
	packages=find_packages(),
	install_requires=['ots.server'],
	entry_points={"ots.publisher_plugin":["publisher_klass = ots.logger_plugin.logger_plugin:LoggerPlugin"]},
	)
