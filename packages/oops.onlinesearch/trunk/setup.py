from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='oops.onlinesearch',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oops'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'pysqlite',
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'paste.app_factory': ['main=oops.onlinesearch:app_factory'],
          },
      )
