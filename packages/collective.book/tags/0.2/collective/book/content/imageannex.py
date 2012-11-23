"""Definition of the ImageAnnex content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import image
from Products.ATContentTypes.content import schemata


from collective.book import BookMessageFactory as _
from collective.book.interfaces import IImageAnnex
from collective.book.config import PROJECTNAME

ImageAnnexSchema = image.ATImageSchema.copy() + atapi.Schema((

    atapi.StringField('picture_type',
            schemata = 'default',
            vocabulary_factory = 'collective.book.picturetypes',
            widget=atapi.SelectionWidget(
                format = 'select',
                description=_(u'help_metadata_picturetypes', 
                    default=u''),
                label=_(u'label_metadata_picturetypes',
                    default=u'Picture type'),
            ),
        ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

schemata.finalizeATCTSchema(
    ImageAnnexSchema,
    moveDiscussion=False
)

class ImageAnnex(image.ATImage):
    implements(IImageAnnex)

    meta_type = "ImageAnnex"
    schema = ImageAnnexSchema
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(ImageAnnex, PROJECTNAME)
