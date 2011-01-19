from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class SearchView(BrowserView):
  def __init__(self, context, request):
    self.context = context
    self.request = request

    
class ITocView(Interface):
  """
  toc view interface
  """

class TocView(BrowserView):
  implements(ITocView)

  def __init__(self, context, request):
    self.context = context
    self.request = request

  @property
  def portal_catalog(self):
      return getToolByName(self.context, 'portal_catalog')

  @property
  def portal(self):
      return getToolByName(self.context, 'portal_url').getPortalObject()
  
  def books(self, full_objects=True):
    """
     Returns all books
    """
    cfilter = {'portal_type': ['Book']}
    return self.context.getFolderContents(contentFilter = cfilter,
                                          full_objects = full_objects)

  def chapters(self, book, full_objects=True):
    """ Returns all chapters and glossaries """
    cfilter = {'portal_type': ['Chapter', 'Glossary']}
    return book.getFolderContents(contentFilter = cfilter,
                                          full_objects = full_objects)
    

class IMoreView(Interface):
  """
  more view interface
  """

class MoreView(BrowserView):
  implements(ITocView)

  def __init__(self, context, request):
    self.context = context
    self.request = request

  @property
  def portal_catalog(self):
      return getToolByName(self.context, 'portal_catalog')

  @property
  def portal(self):
      return getToolByName(self.context, 'portal_url').getPortalObject()
  
  def actions(self):
    actions = 'mobile_actions'
    
    context_state = getMultiAdapter((self.context, self.request),name=u'plone_context_state')
    return context_state.actions().get(actions,None)
    