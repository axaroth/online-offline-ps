"""Definition of the Glossary content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from collective.book import BookMessageFactory as _
from collective.book.interfaces import IGlossary
from collective.book.config import PROJECTNAME

GlossarySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

GlossarySchema['title'].storage = atapi.AnnotationStorage()
GlossarySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    GlossarySchema,
    folderish=True,
    moveDiscussion=False
)

class Glossary(folder.ATFolder):
    """Contains glossary voices"""
    implements(IGlossary)

    meta_type = "Glossary"
    schema = GlossarySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Glossary, PROJECTNAME)
