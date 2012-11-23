"""Definition of the Chapter content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from collective.book import BookMessageFactory as _
from collective.book.interfaces import IChapter
from collective.book.config import PROJECTNAME

ChapterSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ChapterSchema['title'].storage = atapi.AnnotationStorage()
ChapterSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ChapterSchema,
    folderish=True,
    moveDiscussion=False
)

class Chapter(folder.ATFolder):
    """Contains Pages, images and files"""
    implements(IChapter)

    meta_type = "Chapter"
    schema = ChapterSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Chapter, PROJECTNAME)
