import os
import shutil

from zope.component import queryMultiAdapter
from zope.interface import Interface, implements

from oops.staticdump.interfaces import IDumper
from oops.staticdump.interfaces import IExtensionDumper, IExtensionRewriter
from oops.staticdump.utilities import version, Filter


class BaseDumper(object):

    def __init__(self, dumper):
        self.dumper = dumper


class DummyDumper(BaseDumper):

    def dump(self):
        print '-- I am Dummy Dumper (oops)'


class PloneSiteDumper(BaseDumper):

    implements(IExtensionDumper)

    def __init__(self, dumper):
        super(PloneSiteDumper, self).__init__(dumper)
        self.portal = self.dumper.context
        self.filter = Filter(self.portal)

    def dump(self):
        print '-- ext base plone dumper'

        pages = self.filter.public_contents(self.portal.objectValues('ATDocument'))
        for page in pages:
              self.dumper.add_page_html(page)
        self.dumper.update_manifest_with_files()
