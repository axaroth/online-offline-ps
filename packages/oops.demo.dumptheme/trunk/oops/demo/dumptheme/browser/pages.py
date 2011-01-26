from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class IBookPdfView(Interface):
    """
    view interface
    """

    def test():
        """ test method"""


class BookPdfView(BrowserView):
    """
    browser view
    """
    implements(IBookPdfView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def chapters(self, full_objects=True):
      """ Returns all chapters and paragraphs """
      items = []
      cfilter = {'portal_type': ['Chapter']}
      chaps = self.context.getFolderContents(contentFilter = cfilter,full_objects = full_objects)
      
      for chap in chaps:
        cfilter = {'portal_type': ['Paragraph']}
        paragraphs = chap.getFolderContents(contentFilter = cfilter,full_objects = full_objects)
        item = {'title':chap.Title(),
                'paragraphs' : paragraphs}
        
        items.append(item)
      
      return items
    