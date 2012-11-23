"""Definition of the Paragraph content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata


from collective.book import BookMessageFactory as _
from collective.book.interfaces import IParagraph
from collective.book.config import PROJECTNAME

ParagraphSchema = document.ATDocumentSchema.copy()


ParagraphSchema['title'].storage = atapi.AnnotationStorage()
ParagraphSchema['description'].storage = atapi.AnnotationStorage()


class Paragraph(document.ATDocument):
    implements(IParagraph)

    meta_type = "Paragraph"
    schema = ParagraphSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Paragraph, PROJECTNAME)
