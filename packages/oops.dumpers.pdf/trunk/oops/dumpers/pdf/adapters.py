import os

from oops.staticdump import utilities
from oops.staticdump.dumpers.adapters import BaseDumper
from oops.staticdump.interfaces import IDumper
from oops.staticdump.dumpers.adapters import static_base

from zope.interface import implements
from oops.dumpers.pdf.interfaces import IPDFName

from logging import getLogger
LOG = getLogger('oops.dumpers.pdf')


def restore_base(html, base, country_id):
    # restore the url in the links to make it works with pisa pdf generator
    country_path = './%s/'%country_id
    for anchor in html.findAll(['a', 'link']):
        href = anchor.get('href')
        if href is not None:
            href = href.replace(country_path, base+'%s/'%country_id)
            if anchor.name == 'link':
                href = href.replace('./', base)
            anchor['href'] = href

    for img in html.findAll('img'):
        src = img.get('src')
        if src is not None:
            src = src.replace(country_path, base+'%s/'%country_id)
            img['src'] = src

    return html

class HTMLForPDFDumper(BaseDumper):
    implements(IDumper)

    def save_html(self):
        # save the html page from which will be generate the pdf
        # path: <context path>/pdf/index.html
        base = self.file_path('pdf')
        os.mkdir(base)
        try:
            data = self.render_page(view='pdf_view')  # queryMultiAdapter?
        except Exception, e:
            LOG.info('Problem with pdf_view (%s) for: %s'%(e, self.context.absolute_url(relative=1)))
            data = ''
        if data:
            data = restore_base(data, static_base(self.transmogrifier), self.context.id)
        self.save(os.path.join(base, 'index.html'), data)

    def dump(self):
        """ """
        self.save_html()

#
class GenericPDFName(object):

    implements(IPDFName)

    def __init__(self, context):
        self.context = context

    def name(self):
        return '%s.pdf'%self.context.getId()