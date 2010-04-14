from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='oops.demo.dumptheme',
      version=version,
      description="OOPS Demo Dump Theme",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='francesco.merlo@reflab.com',
      url='https://online-offline-ps.googlecode.com/svn/packages/oops.demo.dumptheme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oops', 'oops.demo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
