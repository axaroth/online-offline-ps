from Products.Five import BrowserView
from DateTime.DateTime import DateTime


class UpdateModificationDateView(BrowserView):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def log(self, text):
        self.request.RESPONSE.write("%s\n" %text)

    def __call__(self):

        catalog = self.context.portal_catalog
        today = DateTime()

        self.log("Starting modification date update to '%s'\n" %today)

        for b in catalog():
            obj = b.getObject()
            if obj is not None:
                obj.setModificationDate(today)
                obj.reindexObject(idxs = ['modified', 'ModificationDate'])
                self.log("%s\n\t%s -> %s" %( obj.absolute_url(), obj.modified(),
                                            today))

        self.log("\nCompleted update")
