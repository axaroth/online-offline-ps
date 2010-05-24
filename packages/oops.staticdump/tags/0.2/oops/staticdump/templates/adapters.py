from zope.interface import implements
from oops.staticdump.interfaces import IDataDumper, IAnnexesDataDumper

from Products.CMFCore.utils import getToolByName

class BaseDataDumper:

    implements(IDataDumper)

    def __init__(self, context):
        self.context = context

    def data(self):
        """ """
        return self.context().encode('utf-8', 'ignore')

class SiteDataDumper(BaseDataDumper):

    implements(IDataDumper)

    def data(self):
        """ """
        default_page = self.context.getDefaultPage()
        if default_page:
            html = self.context.unrestrictedTraverse(default_page)()
        else:
            html = self.context()
        return html.encode('utf-8', 'ignore')

class BookDataDumper(BaseDataDumper):

    implements(IDataDumper)

class ChapterDataDumper(BaseDataDumper):

    implements(IDataDumper)

class ImageDataDumper(BaseDataDumper):

    implements(IDataDumper)

    def data(self):
        return self.context.get_data()

class FileDataDumper(BaseDataDumper):

    implements(IDataDumper)

    def data(self):
        return self.context.get_data()

class GlossaryDataDumper(BaseDataDumper):

    implements(IAnnexesDataDumper)
