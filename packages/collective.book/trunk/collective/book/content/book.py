"""Definition of the Book content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from collective.book import BookMessageFactory as _
from collective.book.interfaces import IBook
from collective.book.config import PROJECTNAME

BookSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

BookSchema['title'].storage = atapi.AnnotationStorage()
BookSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    BookSchema,
    folderish=True,
    moveDiscussion=False
)

class Book(folder.ATFolder):
    """Contains Chapters"""
    implements(IBook)

    meta_type = "Book"
    schema = BookSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Book, PROJECTNAME)
