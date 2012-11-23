from Products.Collage.browser.views import BaseView

class BookView(BaseView):
  title = u'Book'

  def chaps(self):
    chaps = []
    catalog = self.context.portal_catalog
    
    for c in catalog(path='/'.join(self.context.getPhysicalPath()),
                    portal_type='Chapter',
                    sort_on='getObjPositionInParent'):
      chaps.append({
              'title': c.Title,
              'url': c.getURL()
      })
    
    return chaps

