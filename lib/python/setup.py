import sys

from setuptools import setup, Extension, find_packages
import setuptools

# Because of relative paths, this must be run from inside ray/lib/python/.

install_requires=[#"numpy",
                  "funcsigs",
                  "protobuf",
                  "colorama",
                  "graphviz",
                  "redis",
                  "cloudpickle"],

#dependency_links=[
#  "https://github.com/cloudpipe/cloudpickle/tarball/0d225a4695f1f65ae1cbb2e0bbc145e10167cce4#egg=cloudpickle-0.2.1"
#]

setup(name="ray",
      version="0.1",
      packages=find_packages(),
      package_data={
        "ray": ["redis-server", "photon_scheduler", "plasma_store", "plasma_manager"]
      },
      zip_safe=False,
      install_requires=install_requires,
      #dependency_links=dependency_links
)
