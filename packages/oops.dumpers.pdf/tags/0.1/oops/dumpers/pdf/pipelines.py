import os
import shutil
import filecmp

from logging import getLogger
LOG = getLogger('oops.dumpers.pdf')

from zope.interface import classProvides, implements
from zope.component import queryMultiAdapter

from Products.CMFCore.utils import getToolByName

from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from oops.staticdump.sections import destination
from oops.staticdump.interfaces import IDumper
from oops.dumpers.pdf.interfaces import IPDFName

from zopyx.smartprintng.client.zip_client import Proxy


class PDFGenerator(object):
    """ Create a pdf file using smartprintng server """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

        self.transmogrifier = transmogrifier
        self.portal = self.transmogrifier.context
        self.dumper = getToolByName(self.portal, 'portal_dumper')
        self.destination = destination(self.transmogrifier)

        if self.dumper.getDumperProperty('pdf', True):
            host = options.get('server', '127.0.0.1')
            port = int(options.get('port', 6543))
            self.proxy = Proxy(host, port)
        else:
            # False must be explicitly assigned
            LOG.info('Disabled')

    def __iter__(self):
        contents = []
        for item in self.previous:

            if self.dumper.getDumperProperty('pdf', True):
                # check if the pdf generation is disabled
                path = item.get('_path')
                obj = self.portal.restrictedTraverse(path)
                adapter = queryMultiAdapter(
                            (obj, self.transmogrifier), name="HTMLForPDFDumper")
                if adapter is not None:
                    adapter.dump()
                    contents.append(item)

            yield item

        for item in contents:
            self.generate_pdf(item)

    def generate_pdf(self, item):
        path = item.get('_path')
        fspath = os.path.join(self.destination, path, 'pdf')

        # can require some control
        name = IPDFName(self.portal.restrictedTraverse(path)).name()
        pdfpath = os.path.join(fspath, name)
        #pdfpath = os.path.join(fspath, 'out.pdf')

        prev_pdfpath = pdfpath.replace('_tmp', '')
        if not self.same_html(item) or not os.path.exists(prev_pdfpath):
            try:
                LOG.info('Conversion start: %s'%path)
                output = self.proxy.convertZIP2(fspath, converter_name='pdf-pisa')
                shutil.move(output['output_filename'], pdfpath)
                LOG.info('Conversion done: %s -> %s'%(path, name))
            except Exception, e:
                LOG.warn('Conversion error: %s'%str(e))
        else:
            if os.path.exists(prev_pdfpath):
                shutil.copyfile(prev_pdfpath, pdfpath)
                LOG.info('Conversion just done: %s'%path)
            else:
                LOG.info('Missing file trying to copy previous pdf: %s -> %s'%(path, name))

    def same_html(self, item):
        path = item.get('_path')
        fspath = os.path.join(self.destination, path, 'pdf', 'index.html')
        prev_fspath = fspath.replace('_tmp', '')
        if os.path.exists(fspath) and os.path.exists(prev_fspath):
            return filecmp.cmp(fspath, prev_fspath)
        else:
            return False