from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='oops.demo.setup',
      version=version,
      description="OOPS Demo Setup",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Francesco Merlo',
      author_email='francesco.merlo@reflab.com',
      url='https://online-offline-ps.googlecode.com/svn/packages/oops.demo.setup',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oops', 'oops.demo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'oops.staticdump',
          'oops.dumpers',
          'collective.book',
          'oops.demo.dumptheme',
          'oops.searchdumpers',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
