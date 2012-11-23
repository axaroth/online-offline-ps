from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Archetypes.utils import shasattr
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class ChapterPicturesView(BrowserView):
  """ """

  def __init__(self, context, request):
    self.context = context
    self.request = request
    self.picture_types = []
    self.results = {}

  def update(self):
      self.title = self.context.Title()
      
      query = {}
      query['portal_type'] = ['ImageAnnex']
      query['path'] = '/'.join(self.context.getPhysicalPath())
      query['sort_on'] = 'sortable_title'
      
      factory = getUtility(IVocabularyFactory, 'collective.book.picturetypes')
      vocabulary = factory(self.context)
      
      catalog = getToolByName(self.context, 'portal_catalog')      
      
      for i in catalog(query):
          obj = i.getObject()
          
          if not shasattr(obj, 'picture_type'):
              #this is not a file extended with document_type field
              continue
              
          dt = obj.picture_type
          
          if not self.results.has_key(dt):
              self.results[dt] = []
              try:
                  term = vocabulary.getTermByToken(dt)
                  dt_label = term.title
              except LookupError:
                  dt_label = dt
                            
              self.picture_types.append( (dt_label, dt) )
          
          try:
              chapter = obj.aq_parent
              part = chapter.aq_parent
              section = "%s / %s" %(part.Title(), chapter.Title())
              section_url = chapter.absolute_url()
              field = obj.getField('image')
              format = self.context.lookupMime(field.getContentType(obj))
              size = obj.get_size()
          except:
              section = ''
              section_url = '#'
              date = ''
              format = ''
              size = ''
          
          if type(size) == int:
              size_kb = size / 1024
          else:
              size_kb = '0'
                 
          self.results[dt].append({
            'title': obj.Title(),
            'url': obj.absolute_url(),
            'description': obj.Description(),
            'section': section,
            'section_url': section_url,
            'date': self.context.toLocalizedTime(obj.modified()),
            'format': format,
            'size': '%sKb' %size_kb,
            'img_tag': obj.tag(scale='tile'),
          })
      
      self.picture_types.sort()
