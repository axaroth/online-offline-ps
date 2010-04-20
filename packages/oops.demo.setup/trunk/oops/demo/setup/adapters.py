from zope.interface import Interface, implements
from oops.staticdump.interfaces import IExtensionDumper


class BaseDumper(object):

    def __init__(self, dumper):
        self.dumper = dumper


class PloneSiteDumper(BaseDumper):

    implements(IExtensionDumper)

    def dump(self):
        print '-- oops.demo plone extension dumper'
        self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'search_results.html',
                        view='search_results.html')
        self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'offline.html',
                        view='offline.html')
