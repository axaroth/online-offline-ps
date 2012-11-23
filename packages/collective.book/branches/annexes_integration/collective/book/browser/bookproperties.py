from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope import schema
from zope.formlib.form import FormFields
from zope.schema import ValidationError

from plone.app.controlpanel.form import ControlPanelForm
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode


class IBookPropertiesSchema(Interface):
    
    document_types = schema.List(
        title=_(u'Document Types'),
        description=_(u""),
        required=True,
        value_type=schema.TextLine(),
    )
    
    picture_types = schema.List(
        title=_(u'Picture Types'),
        description=_(u""),
        required=True,
        value_type=schema.TextLine(),
    )

class BookPropertiesControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IBookPropertiesSchema)
    
    def __init__(self, context):
        super(BookPropertiesControlPanelAdapter, self).__init__(context)
        self.portal = context
        self.pprop = getToolByName(self.portal, 'portal_properties').book_properties
        if not self.pprop.hasProperty('document_types_vocabulary'):
            self.pprop._setProperty('document_types_vocabulary',[],'lines')
        if not self.pprop.hasProperty('picture_types_vocabulary'):
            self.pprop._setProperty('picture_types_vocabulary',[],'lines')
    
    def get_document_types(self):
        return getattr(self.pprop, 'document_types_vocabulary', [])

    def set_document_types(self, values):
        self.pprop._updateProperty('document_types_vocabulary',values)
    
    def get_picture_types(self):
        return getattr(self.pprop, 'picture_types_vocabulary', [])

    def set_picture_types(self, values):
        self.pprop._updateProperty('picture_types_vocabulary',values)


    document_types = property(get_document_types, set_document_types)
    picture_types = property(get_picture_types, set_picture_types)

class BookPropertiesControlPanel(ControlPanelForm):

    form_fields = FormFields(IBookPropertiesSchema)
    label = _("Book Properties vocabularies")
    description = _("Control Panel to manage metadata vocabularies for File Annexes and Image Annexes")
    form_name = _("Metadata Vocabularies")
