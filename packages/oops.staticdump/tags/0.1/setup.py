from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='oops.staticdump',
      version=version,
      description="Create a static dump of a site containing collective.book",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Reflab srl',
      author_email='info@reflab.it',
      url='http://code.google.com/p/online-offline-ps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['oops'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.transmogrifier',
          'plone.app.transmogrifier',
          'BeautifulSoup',
          'simplejson',
      ],
      entry_points=""" """,
      )
