from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.book import BookMessageFactory as _


class IBook_tocView(Interface):
    """
    book_toc view interface
    """

    def test():
        """ test method"""


class Book_tocView(BrowserView):
    """
    book_toc browser view
    """
    implements(IBook_tocView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def contents(self, full_objects=True):
        """
         Returns all chapters and glossaries
        """
        cfilter = {'portal_type': ['Chapter', 'Glossary']}
        return self.context.getFolderContents(contentFilter = cfilter,
                                              full_objects = full_objects)
