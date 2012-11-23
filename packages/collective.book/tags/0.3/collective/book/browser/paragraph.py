from Acquisition import aq_inner
from Products.Five import BrowserView

class ParagraphView(BrowserView): 
    """ A simple redirect to the chapter view with an anchor """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        parent_url = aq_inner(self.context).aq_parent.absolute_url()
        dest = "%s#%s" %(parent_url, self.context.getId())
        self.request.RESPONSE.redirect(dest)
