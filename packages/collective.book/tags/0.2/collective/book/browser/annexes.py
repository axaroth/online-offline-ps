from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Acquisition import aq_inner
from Products.Archetypes.utils import shasattr
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class ChapterAnnexesView(BrowserView):
  """ """

  def __init__(self, context, request):
    self.context = context
    self.request = request
    self.document_types = []
    self.results = {}

  def update(self):
      self.title = self.context.Title()
      
      query = {}
      query['portal_type'] = ['FileAnnex']
      query['path'] = '/'.join(self.context.getPhysicalPath())
      query['sort_on'] = 'sortable_title'
      
      factory = getUtility(IVocabularyFactory, 'collective.book.documenttypes')
      vocabulary = factory(self.context)
      
      catalog = getToolByName(self.context, 'portal_catalog')      
      
      for i in catalog(query):
          obj = i.getObject()
          
          if not shasattr(obj, 'document_type'):
              #this is not a file extended with document_type field
              continue
              
          dt = obj.document_type
          
          if not self.results.has_key(dt):
              self.results[dt] = []
              try:
                  term = vocabulary.getTermByToken(dt)
                  dt_label = term.title
              except LookupError:
                  dt_label = dt
                            
              self.document_types.append( (dt_label, dt) )
          
          try:
              chapter = obj.aq_parent
              part = chapter.aq_parent
              section = "%s / %s" %(part.Title(), chapter.Title())
              section_url = chapter.absolute_url()
              field = obj.getField('file')
              format = self.context.lookupMime(field.getContentType(obj))
              size = obj.get_size()/1024
          except:
              section = ''
              section_url = '#'
              date = ''
              format = ''
              size = '-'
              
          self.results[dt].append({
            'title': obj.Title(),
            'url': obj.absolute_url(),
            'description': obj.Description(),
            'section': section,
            'section_url': section_url,
            'date': self.context.toLocalizedTime(obj.modified()),
            'format': format,
            'size': '%sKb' % size,
          })
      
      self.document_types.sort()
      

class FileAnnexView(BrowserView): 

    FIELD_FOR_ANCHOR = 'document_type'
    VIEW = 'annexes'
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        parent_url = aq_inner(self.context).aq_parent.absolute_url()
        anchor = self.context.getField(self.FIELD_FOR_ANCHOR).get(self.context) 
        dest = "%s/%s#%s" %(parent_url, self.VIEW, anchor)
        self.request.RESPONSE.redirect(dest)      
        

class ImageAnnexView(FileAnnexView): 
    """ A simple redirect to the annexs view with an anchor """

    FIELD_FOR_ANCHOR = 'picture_type'
    VIEW = 'pictures'
        
