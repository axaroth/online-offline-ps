from zope.interface import Interface, implements
from oops.staticdump.interfaces import IExtensionDumper
from oops.staticdump import utilities


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
        self.dumper.manifest_data.remove_entry('search_results.html')
        self.dumper.manifest_data.add_entry('search_results.html',
                                            utilities.version(self.dumper.context),
                                            ignoreQuery=True)
        self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'offline.html',
                        view='offline.html')
        
        try:
            #view available on mobile theme
            self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'toc.html',
                        view='toc_view')
            
            #view available on mobile theme
            self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'more.html',
                        view='more_view')
        except:
            print '-- BrowserView not found'
