from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName


class BookPropertiesVocabulary(object):
    implements(IVocabularyFactory)
    
    def __init__(self,name):
        self.name = name
    
    def __call__(self, context):
        context = getattr(context, 'context', context)
        properties = getToolByName(context, 'portal_properties')
        vocabularies = getattr(properties, 'book_properties')
        voc = vocabularies.getProperty(self.name)
        
        items = []
        for v in voc:
            if v!='': 
                items.append(v.split('|')) 
        
        items = [SimpleTerm(i[0].strip(), i[0].strip(), i[1].strip()) for i in items] #SimpleTerm(self, value, token=None, title=None):
        
        
        return SimpleVocabulary(items)


DTVocabularyFactory = BookPropertiesVocabulary("document_types_vocabulary")
PTVocabularyFactory = BookPropertiesVocabulary("picture_types_vocabulary")

