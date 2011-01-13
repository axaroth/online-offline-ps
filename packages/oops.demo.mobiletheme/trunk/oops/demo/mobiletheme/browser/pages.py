from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class SearchView(BrowserView):
  def __init__(self, context, request):
    self.context = context
    self.request = request
