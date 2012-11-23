"""Definition of the Voice content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from collective.book import BookMessageFactory as _
from collective.book.interfaces import IVoice
from collective.book.config import PROJECTNAME

VoiceSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

VoiceSchema['title'].storage = atapi.AnnotationStorage()
VoiceSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VoiceSchema, moveDiscussion=False)

class Voice(base.ATCTContent):
    """Glossary voice"""
    implements(IVoice)

    meta_type = "Voice"
    schema = VoiceSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Voice, PROJECTNAME)
