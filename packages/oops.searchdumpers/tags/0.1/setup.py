from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='oops.searchdumpers',
      version=version,
      description="Create a static dump of terms site for fulltext search using sqlite",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Reflab s.r.l.',
      author_email='info@reflab.com',
      url='http://online-offline-ps.googlecode.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oops'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pysqlite',
          'oops.staticdump',
          'simplejson',
          'zope.interface',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
