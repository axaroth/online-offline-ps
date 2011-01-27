from plone.app.layout.viewlets import common
from oops.dumpers.pdf.interfaces import IPDFName

class GlobalSectionsViewlet(common.GlobalSectionsViewlet):

    def update(self):
        super(GlobalSectionsViewlet, self).update()
        self.selected_portal_tab = 'index_html'

        # customized in order to enable the 'selected' class even w/o request
        # for the static version
        # XXX this is not the best way to fix this problem
        for tab in self.portal_tabs:
            if tab['id'] == 'index_html': continue
            if self.context.absolute_url().startswith(tab['url']):
                self.selected_portal_tab = tab['id']
                break

class PdfViewlet(common.ViewletBase):

    def update(self):
        super(PdfViewlet, self).update()

        self.visible = False
        if self.context.portal_type == 'Book':
            self.visible = True
            self.url = self.context.absolute_url()

    def pdfname(self):
        return IPDFName(self.context).name()


