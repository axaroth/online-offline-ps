"""Definition of the FileAnnex content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import file
from Products.ATContentTypes.content import schemata


from collective.book import BookMessageFactory as _
from collective.book.interfaces import IFileAnnex
from collective.book.config import PROJECTNAME

FileAnnexSchema = file.ATFileSchema.copy() + atapi.Schema((

    atapi.StringField('document_type',
            schemata = 'default',
            vocabulary_factory = 'collective.book.documenttypes',
            widget=atapi.SelectionWidget(
                format = 'select',
                description=_(u'help_metadata_documenttype', 
                    default=u''),
                label=_(u'label_metadata_documenttype',
                    default=u'Document type'),
            ),
        ),

))


schemata.finalizeATCTSchema(
    FileAnnexSchema,
    moveDiscussion=False
)

class FileAnnex(file.ATFile):
    implements(IFileAnnex)

    meta_type = "FileAnnex"
    schema = FileAnnexSchema


atapi.registerType(FileAnnex, PROJECTNAME)
