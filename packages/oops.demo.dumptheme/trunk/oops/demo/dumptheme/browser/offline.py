from Products.Five import BrowserView


class OfflinePanelView(BrowserView):
  """ """

  def __init__(self, context, request):
    self.context = context
    self.request = request


  def books(self):
      return self.context.getFolderContents(contentFilter={'portal_type':'Book'},
          full_objects=True)
      
  def chapters(self, book):
      return book.getFolderContents(contentFilter={'portal_type':'Chapter'},
          full_objects=True)
