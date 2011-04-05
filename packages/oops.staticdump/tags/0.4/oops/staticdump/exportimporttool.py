"""Based on Plone Properties tool setup handlers. """

from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers

_BASE = 'staticdumpertool.xml'
_PROPERTIES = 'staticdumpertoolproperties.xml'

class DumperXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):

    """XML im- and exporter for Dumper tool properties.
    (Copied from Products.CMFCore.exportimport.properties.PropertiesXMLAdapter)
    """

    _LOGGER_ID = 'staticdumpertool'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        self._encoding = self.context.getProperty('default_charset', 'utf-8')

        node = self._doc.createElement('dumpertool')
        node.appendChild(self._extractProperties())

        self._logger.info('StaticDumper properties exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        self._encoding = self.context.getProperty('default_charset', 'utf-8')

        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
            if child.getAttribute('name') != 'default_charset':
                continue
            self._encoding = self._getNodeText(child) or 'utf-8'
            break

        # Raise an error on 'dumper' property. Why?
        #if self.environ.shouldPurge():
            #self._purgeProperties()

        self._initProperties(node)

        self._logger.info('StaticDumper properties imported.')

def importStaticDumper(context):
    """ Import staticdumper tool.
    """
    site = context.getSite()
    logger = context.getLogger('staticdumpertool')
    ptool = getToolByName(site, 'portal_dumper', None)

    if ptool is None:
        logger.info('Nothing to import.')
        return    

    # tool
    body = context.readDataFile(_BASE)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = DumperXMLAdapter(ptool, context)
    importer.body = body

    # property sheets
    body = context.readDataFile(_PROPERTIES)
    if body is None:
        logger.info('Nothing to import.')
        return

    importer = queryMultiAdapter((ptool, context), IBody)
    if importer is None:
        logger.warning('Import adapter missing.')
        return

    importer.body = body
    logger.info('StaticDumper dumpers properties imported.')

    logger.info('StaticDumper tool imported.')

def exportStaticDumper(context):
    """ Export staticdumper tool.
    """
    site = context.getSite()
    logger = context.getLogger('staticdumpertool')
    ptool = getToolByName(site, 'portal_dumper', None)
    if ptool is None:
        logger.info('Nothing to export.')
        return

    # tool
    exporter = DumperXMLAdapter(ptool, context)
    context.writeDataFile(_BASE, exporter.body, exporter.mime_type)

    # property sheets
    exporter = queryMultiAdapter((ptool, context), IBody)

    if exporter is None:
        logger.warning('Export adapter missing.')
        return

    context.writeDataFile(_PROPERTIES, exporter.body, exporter.mime_type)
    logger.info('StaticDumper properties exported.')

    logger.info('StaticDumper tool exported.')
