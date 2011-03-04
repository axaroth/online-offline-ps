from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner

from oops.staticdump.utilities import external_url

class LogoViewlet(common.LogoViewlet):
  render =  ViewPageTemplateFile('templates/logo.pt')

  def update(self):
    super(LogoViewlet, self).update()


class FooterViewlet(common.ViewletBase):
  render = ViewPageTemplateFile('templates/footer.pt')

  def update(self):
    super(FooterViewlet, self).update()
    site_url = external_url(self.context)
    more = site_url + '/more.html'
    search = site_url + '/search_results.html'
    toc = site_url + '/toc.html'
    self.actions = [
      {'url': site_url, 'title': 'Home', 'id': 'grid'},
      {'url': toc, 'title': 'TOC', 'id': 'setup'},
      {'url': more, 'title': 'More', 'id': 'info'},
      {'url': search, 'title': 'Search', 'id': 'search'},
    ]

    self.visible = True
