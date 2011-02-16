import transaction

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.PropertyManager import PropertyManager

from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.PropertiesTool import PropertiesTool
from Products.CMFPlone.interfaces import IPropertiesTool


class DumperTool(PropertiesTool):
    """ This tool provides a common interface for accessing "dumper"
    configurations"""

    id = 'portal_dumper'
    title = 'Dumper Tool'
    dumper = 'default'

    toolicon = 'skins/plone_images/topic_icon.png'

    meta_type = 'StaticDumper Properties Tool'
    meta_types = ((
        {'name' : 'Plone Property Sheet',
         'action' : 'manage_addPropertySheetForm'
         },
        ))

    implements(IPropertiesTool)

    manage_options = (
        {'action': 'manage_main', 'label': 'Contents'},
        {'action': 'manage_propertiesForm', 'label': 'Properties'},
        {'action': 'manage_access', 'help': ('OFSP', 'Security.stx'), 'label': 'Security'},
        {'action': 'manage_interfaces', 'label': 'Interfaces'},
        {'action': 'manage_migrate', 'label': 'Migrate'},
    )
    _properties = (
        {'type': 'string', 'id': 'title', 'mode': 'wd'},
         {'type': 'string', 'id': 'dumper', 'mode': 'wd'},
    )

    security = ClassSecurityInfo()

    def _p_resolveConflict(self, oldState, savedState, newState):
          """ This is due to a concurrent call to dumper.
              The previous transaction is running so the call to status
              try to write the property but generate a conflict.
          """
          if oldState['running'] == True and newState['running'] == False:
              oldState['running'] = False
          return oldState

    security.declareProtected(ManagePortal, 'getDumperProperty')
    def getDumperProperty(self, name, default=''):
        dumper_id = self.getProperty('dumper')
        return self[dumper_id].getProperty(name, default)

    security.declareProtected(ManagePortal, 'setDumper')
    def setDumper(self, id):
        """ Set dumper id """
        if id in self.objectIds():
            self._updateProperty('dumper', id)
        else:
            raise Exception('Wrong Dumper id')

    security.declareProtected(ManagePortal, 'status')
    def status(self, status=None):
        """ status of dumper """
        if status is None:
            return self.getProperty('running')
        else:
            self._updateProperty('running', status)
            transaction.commit()
            return status

    security.declareProtected(ManagePortal, 'manage_migrate')
    def manage_migrate(self, REQUEST=None):
        """ Migrate the dumper properties in the portal_properties tool """
        from Products.CMFCore.utils import getToolByName
        name = 'dumper_properties'

        props = getToolByName(self, 'portal_properties')
        if props.hasObject(name):
            o = props._getOb(name)
            o.title = 'Migrated Dumper'
            self._setObject('migrated_dumper', o)
            props._delObject(name)
            if REQUEST is not None:
                return REQUEST.RESPONSE.redirect(
                                  self.absolute_url()
                                  + '/manage_main'
                                  + '?manage_tabs_message=Migrated Old Dumper properties.'
                              )
        elif REQUEST is not None:
            return REQUEST.RESPONSE.redirect(
                              self.absolute_url()
                              + '/manage_main'
                              + '?manage_tabs_message=Nothing to migrate.'
                          )

    def addPropertySheet(self, id, title='', propertysheet=None):
        """ Add a new PropertySheet Dumper properties
        """
        pm = PropertyManager()
        pm._setProperty('filesystem_target', '', 'string')
        pm._setProperty('html_base', '', 'string')
        pm._setProperty('theme', '', 'string')
        pm._setProperty('dump_configuration_name', '', 'string')
        pm._setProperty('theme_folders', [], 'lines')
        pm._setProperty('file_types', ['File',], 'lines')
        pm._setProperty('image_types', ['Image',], 'lines')
        #pm._setProperty('running', title, 'string')
        PropertiesTool.addPropertySheet(self, id, title=title, propertysheet = pm)


InitializeClass(DumperTool)
