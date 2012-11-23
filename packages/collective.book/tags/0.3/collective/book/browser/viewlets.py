from plone.app.layout.viewlets import common
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Archetypes.utils import shasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class AnnexesTocViewlet(common.ViewletBase):
  render =  ViewPageTemplateFile('templates/annexes_toc.pt')
  
  def update(self):
      super(AnnexesTocViewlet, self).update()

      self.document_types = []
      self.annexes_url = self.context.absolute_url() + '/annexes'

      query = {}
      query['portal_type'] = ['FileAnnex']
      query['path'] = '/'.join(self.context.getPhysicalPath())
      
      factory = getUtility(IVocabularyFactory, 'collective.book.documenttypes')
      vocabulary = factory(self.context)
      
      catalog = getToolByName(self.context, 'portal_catalog')      
      
      found_dts = {}
      
      for i in catalog(query):
          obj = i.getObject()
          
          if not shasattr(obj, 'document_type'):
              #this is not a file extended with document_type field
              continue
              
          dt = obj.document_type
          
          if not found_dts.has_key(dt):
              found_dts[dt] = None
              try:
                  term = vocabulary.getTermByToken(dt)
                  found_dts[dt] = term.title
              except LookupError:
                  found_dts[dt] = dt
                            
      self.document_types = found_dts.items()
      self.document_types.sort()   


class PicturesTocViewlet(common.ViewletBase):
  render =  ViewPageTemplateFile('templates/pictures_toc.pt')
  
  def update(self):
      super(PicturesTocViewlet, self).update()

      self.picture_types = []
      self.pictures_url = self.context.absolute_url() + '/pictures'

      query = {}
      query['portal_type'] = ['ImageAnnex']
      query['path'] = '/'.join(self.context.getPhysicalPath())
      
      factory = getUtility(IVocabularyFactory, 'collective.book.picturetypes')
      vocabulary = factory(self.context)
      
      catalog = getToolByName(self.context, 'portal_catalog')      
      
      found_pts = {}
      
      for i in catalog(query):
          obj = i.getObject()
          
          if not shasattr(obj, 'picture_type'):
              #this is not an image extended with picture_type field
              continue
              
          pt = obj.picture_type
          
          if not found_pts.has_key(pt):
              found_pts[pt] = None
              try:
                  term = vocabulary.getTermByToken(pt)
                  found_pts[pt] = term.title
              except LookupError:
                  found_pts[pt] = pt
                            
      self.picture_types = found_pts.items()
      self.picture_types.sort() 
