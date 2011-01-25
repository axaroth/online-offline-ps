import os
import shutil
import filecmp

from logging import getLogger
LOG = getLogger('oops.dumpers.pdf')

from zope.interface import classProvides, implements
from zope.component import queryMultiAdapter

from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from oops.staticdump.sections import destination
from oops.staticdump.interfaces import IDumper

from zopyx.smartprintng.client.zip_client import Proxy


class PDFGenerator(object):
    """ Create a pdf file using smartprintng server """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

        self.transmogrifier = transmogrifier
        self.portal = self.transmogrifier.context
        self.destination = destination(self.transmogrifier)

        host = options.get('server', '127.0.0.1')
        port = int(options.get('port', 6543))
        self.proxy = Proxy(host, port)

    def __iter__(self):
        countries = []
        for item in self.previous:
            path = item.get('_path')
            obj = self.portal.restrictedTraverse(path)
            adapter = queryMultiAdapter(
                        (obj, self.transmogrifier), name="HTMLForPDFDumper")
            if adapter is not None:
                adapter.dump()
                countries.append(item)
            yield item

        for item in countries:
            self.generate_pdf(item)

    def generate_pdf(self, item):
        path = item.get('_path')
        fspath = os.path.join(self.destination, path, 'pdf')
        pdfpath = os.path.join(fspath, 'out.pdf')
        prev_pdfpath = pdfpath.replace('_tmp', '')
        if not self.same_html(item) or not os.path.exists(prev_pdfpath):
            try:
                LOG.info('PDFGenerator conversion start: %s'%path)
                output = self.proxy.convertZIP2(fspath, converter_name='pdf-pisa')
                shutil.move(output['output_filename'], pdfpath)
                LOG.info('PDFGenerator conversion done: %s'%path)
            except Exception, e:
                LOG.warn('PDFGenerator conversion error: %s'%str(e))
        else:
            if os.path.exists(prev_pdfpath):
                shutil.copyfile(prev_pdfpath, pdfpath)
                LOG.info('PDFGenerator conversion just done: %s'%path)
            else:
                LOG.info('PDFGenerator missing file trying to copy previous pdf: %s'%path)

    def same_html(self, item):
        path = item.get('_path')
        fspath = os.path.join(self.destination, path, 'pdf', 'index.html')
        prev_fspath = fspath.replace('_tmp', '')
        if os.path.exists(fspath) and os.path.exists(prev_fspath):
            return filecmp.cmp(fspath, prev_fspath)
        else:
            return False