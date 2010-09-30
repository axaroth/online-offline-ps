from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFPlone.PropertiesTool import PropertiesTool
from Products.CMFPlone.interfaces import IPropertiesTool


class DumperTool(PropertiesTool):
    """ This tool provides a common interface for accessing "dumper" configurations"""

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
    )
    _properties = (
        {'type': 'string', 'id': 'title', 'mode': 'wd'},
         {'type': 'string', 'id': 'dumper', 'mode': 'wd'},
    )

    security = ClassSecurityInfo()


InitializeClass(DumperTool)
