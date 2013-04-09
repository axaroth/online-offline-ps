import os, shutil
import urlparse
import simplejson as json

from zope.annotation.interfaces import IAnnotations
from zope.interface import directlyProvides, directlyProvidedBy
from zope.interface import Interface, implements, alsoProvides
from zope.component.interface import searchInterface
from zope.component import queryUtility
from zope.publisher.interfaces.browser import IBrowserSkinType

from Products.CMFCore.interfaces import IFolderish
from Products.Archetypes.interfaces import IBaseFolder

from Products.CMFCore.utils import getToolByName
from zope.component import queryAdapter, getAdapters

from BeautifulSoup import BeautifulSoup
from oops.staticdump.interfaces import IDumper, IDataDumper, IExtensionDumper, \
                                       IUrlRewriter, ISearchDataDumper, \
                                       ILanguageDumper

from oops import staticdump
from oops.staticdump import utilities

import mimetypes
import urllib

from logging import getLogger
LOG = getLogger('oops.staticdump')

IMAGE_SIZES = ['large', 'preview', 'mini', 'thumb', 'tile', 'icon', 'listing']


class Manifest(object):
    """ Google Gears compatible manifest """

    def __init__(self):
        """ model manifest.json """
        self.version = ''
        self.entries = []

    def add_entry(self, id, date, src=None, redirect=None, ignoreQuery=None,
                 matchQuery=None):
        self.update_version(date)

        entry = {'url':'./%s'%id}

        if src and redirect:
            raise KeyError, "src and redirect are exclusive options"
        if src is not None:
            entry['src'] = src
        if redirect is not None:
            entry['redirect'] = redirect

        if ignoreQuery and matchQuery:
            raise KeyError, "ignoreQuery and matchQuery are exclusive options"
        if ignoreQuery is not None:
            entry['ignoreQuery'] = ignoreQuery
        if matchQuery is not None:
            entry['matchQuery'] = matchQuery

        self.entries.append(entry)

    def remove_entry(self, id):
        for entry in self.entries:
            if entry.get('url') == './%s'%id:
                self.entries.remove(entry)

    def update_version(self, version):
        """ version is a date in '%Y-%m-%d %H:%M' format """
        if version > self.version:
            self.version = version

    def __call__(self):
        """ return manifest.json string """
        data = {}
        data['betaManifestVersion'] = 1
        data['version'] = self.version
        data['entries'] = self.entries
        return json.dumps(data)


class HTML5Manifest(object):
    """ HTML5 compatible manifest """

    def __init__(self, version):
        """  """
        self.version = version
        self.entries = []
        self.fallbacks = []

    def add_entry(self, id):
        # to review
        entry = {'url':'./resources_%s/%s'%(self.version, id)}
        self.entries.append(entry)

    def add_fallback(self, url, fallback_url):
        #
        entry = {'url': url}
        entry = {'fallback': fallback_url}
        self.fallbacks.append(entry)

    def __call__(self):
        """ return manifest """
        data =  []
        data.append("CACHE MANIFEST")
        data.append("# version: %s\n"%self.version)
        for entry in self.entries:
            data.append('%s'%entry['url'])
        # FALLBACK
        if len(self.fallbacks) > 0:
            data.append("FALLBACK:")
            for entry in self.fallbacks:
                data.append('%s %s'%(entry['url'], entry['fallback']))
        # NETWORK
        data.append("\n")
        data.append("NETWORK:")
        data.append("*")
        return '\n'.join(data)

#
def static_base(transmogrifier):
    base = transmogrifier['transmogrifier'].get('static_base')
    if not base.endswith('/'):
        return base + '/'
    else:
        return base
#

class BaseDumper(object):

    implements(IDumper)

    def __init__(self, context, transmogrifier):
        self.context = context
        self.transmogrifier = transmogrifier

        #
        self.static_base = static_base(transmogrifier)
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.dumper = getToolByName(self.portal, 'portal_dumper')

        self.path = '/'.join(self.context.getPhysicalPath()[2:]) # remove portal id
        try:
            self.parent_path = '/'.join(self.context.aq_parent.getPhysicalPath()[2:])
        except:
            self.parent_path = ''

        # destination paths for dumpers
        self.destination = transmogrifier['transmogrifier'].get('destination', '/tmp/dump')
        self.version = self.dumper.getDumperProperty('version', '0')
        self.resources_destination = os.path.join(self.destination, 'resources_%s'%self.version)

        # Manifests
        self.manifest_data = Manifest()
        self.manifest_html5 = HTML5Manifest(self.version)

        self.theme = self.dumper.getDumperProperty('theme')
        self.search_data = {}


    def render_page(self, context=None, view=None):

        if context is None:
            context = self.context

        if view is None:
            view = context.getDefaultPage()

        request = getattr(self.portal.getPhysicalRoot(), 'REQUEST', None)

        # language
        # monkey patch the LANGUAGE_TOOL instance inside the request with
        # or custom accessor to language bindings
        def customGetLanguageBindings():
            language_bindings = ('en', 'en', ['en',])
            language_dumper = queryAdapter(context, ILanguageDumper)
            if language_dumper is not None:
                i18n_language = language_dumper.i18n_language()
                language_bindings = (i18n_language, i18n_language, [i18n_language,])
            return language_bindings

        originalGetLanguageBindings = request.LANGUAGE_TOOL.getLanguageBindings
        request.LANGUAGE_TOOL.getLanguageBindings = customGetLanguageBindings

        # current skin
        current_skin = self.portal.getCurrentSkinName()
        current_skin_iface = queryUtility(IBrowserSkinType, name=current_skin)

        # dump skin
        dump_skin_iface = queryUtility(IBrowserSkinType, name=self.theme)

        # switch skin and layer
        self.portal.changeSkin(self.theme, request)

        old_interfaces = directlyProvidedBy(request)
        new_interfaces = directlyProvidedBy(request)
        if current_skin_iface is not None and current_skin_iface in new_interfaces:
            new_interfaces = new_interfaces - current_skin_iface

        if dump_skin_iface is not None and dump_skin_iface not in new_interfaces:
            new_interfaces = dump_skin_iface + new_interfaces

        directlyProvides(request, new_interfaces)

        #
        to_be_rendered = context
        if view is not None:
            sm = utilities.ReplaceSecurityManager(context, context.unrestrictedTraverse)
            to_be_rendered = sm.doItAs(utilities.USER, view)

        sm = utilities.ReplaceSecurityManager(context, to_be_rendered.__call__)
        data = sm.doItAs(utilities.USER)

        # modify HTML
        html = BeautifulSoup(data.encode('utf-8', 'ignore'))
        self.replace_base(html)
        self.rewrite_links(html, context)
        if self.dumper.getDumperProperty('html5', False):
            self.add_html5manifest(html)

        # restore skin and layer
        self.portal.changeSkin(current_skin, request)
        directlyProvides(request, old_interfaces)

        # restore original accessor to language bindings
        request.LANGUAGE_TOOL.getLanguageBindings = originalGetLanguageBindings

        #remove memoize annotations on request
        request_annotations = IAnnotations(request)
        for annotation_key in ['plone.memoize', 'plone.memoize_request',
                               'pts.memoize', 'pts.memoize_second']:
            if annotation_key in request_annotations.keys():
                del request_annotations[annotation_key]

        return html

    def getRelativeContentPath(self, content):
        portal_url = self.portal.portal_url
        path = '/'+'/'.join(portal_url.getRelativeContentPath(content))
        if IFolderish.providedBy(content) or IBaseFolder.providedBy(content):
            path += '/index.html'
        return path

    def rewrite_links(self, html, context):
        portal_id = self.portal.id
        portal_url = self.portal.absolute_url()

        # remove edit links
        for anchor in html.findAll('a', attrs={'class': 'edit'}):
            anchor.extract()

        # remove script tags
        for tag in html.findAll('script'):
            if tag.get('dump') != 'true':
                tag.extract()

        # remove style tags
        for tag in html.findAll('style'):
            tag.extract()

        # remove link tags
        for tag in html.findAll('link'):
            if tag.get('rel') != 'stylesheet':
                tag.extract()

        # scripts
        for script in html.findAll('script'):
            src = script.get('src')
            if src is not None:
                src = src.replace(portal_url,'.')
                script['src'] = src

        # anchors
        for anchor in html.findAll(['a', 'link', 'area']):

            # don't try to rewrite the url
            if anchor.get('rel') == 'external':
                continue

            href = anchor.get('href')

            if href is not None and not utilities.is_external(context, href):
                # this code _must_ be refactored

                # fix the ATFile link
                if '/at_download/file' in href:
                    href = href.replace('/at_download/file', '')

                href = urllib.unquote(href)
                # rewrite internal anchors in order to be absolute
                if href.startswith('#'):
                    href = context.absolute_url() + href

                # convert the url in order to have the full zope path
                if href.startswith(portal_url):
                    # 1) common case
                    href = href.replace(portal_url, '/'+portal_id)
                elif href.startswith('/') and len(portal_url.split('/')) > 3:
                    # 2) this is a subsite
                    subpath = '/'+'/'.join(portal_url.split('/')[3:])
                    href = href.replace(subpath, '/'+portal_id)
                else:
                    # try to get a content (works for relative url)
                    obj = utilities.is_object_in(context, href)
                    if obj is not None and hasattr(obj, 'getPhysicalPath'):
                        href = '/'.join(obj.getPhysicalPath()) #?
                    else:
                        LOG.info('rewrite_links: not converted: %s'%href)

                # rewrite internal links
                if href.startswith('/'):
                    try:
                        # remove internal anchor
                        if '#' in href:
                            href, sharp = href.split('#')
                        else:
                            sharp = ''

                        obj = self.portal.unrestrictedTraverse(
                                                    str(href).lstrip('/'), None)

                        # rewrite content link using the UrlRewriter adapter
                        if obj is not None:
                            rewriter = IUrlRewriter(obj)
                            href = rewriter.rewrite_anchor(href)

                        # and add again internal anchor
                        if sharp:
                            href += '#%s'%sharp

                    except Exception, e:
                        LOG.info(str(e))

                # remove portal id
                if portal_id == href[1:len(portal_id)+1]:
                    href = href[len(portal_id)+1:]

                # add . to have relative link to base href
                if href.startswith('/'):
                    href = '.' + href

                # set also the mimetype as attribute
                mimetype = mimetypes.guess_type(href, strict=False)[0]
                if mimetype and mimetype != 'text/html':
                    anchor['data-mimetype'] = mimetype
                anchor['href'] = href

        # images
        for img in html.findAll('img'):
            src = img.get('src')
            
            if src is not None and not utilities.is_external(context, src):
                src = urllib.unquote(src)

                obj = utilities.is_object_in(context, src)
                if obj is None:
                    LOG.info('rewrite_links: no method or property for: %s'%src)
                else:

                    src = '/'.join(obj.getPhysicalPath())
                    # src now is a physical path with portal_id in it

                    # if src is a field of a non image content, the code below
                    # about 'replace size' doesn't work

                    # replace size
                    name, size = utilities.image_name_size_from(src)
                    if name:
                        field_name, size_value = utilities.parse_size(size)

                        if size_value is not None:
                            new_name =  utilities.new_name(src)
                            old_name = '/%s/%s'%(name, size)
                            src = src.replace(old_name, new_name)

                        width, height = utilities.image_dimensions(obj, field_name, size_value)
                        if width and height:
                            if not img.has_key('width'):
                                img['width'] = '%ipx'%width
                            if not img.has_key('height'):
                                img['height'] = '%ipx'%height

                        # remove portal id
                        if src.startswith('/' + portal_id + '/'):
                            src = src[len('/'+portal_id):]
                        elif src == '/'+portal_id:
                            src = '/'

                        # add . to have relative link to base href
                        if src[0] == '/':
                            src = '.' + src

                        img['src'] = urllib.quote(src)
                    else:
                        # remove portal id
                        if src.startswith('/' + portal_id + '/'):
                            src = src[len('/'+portal_id):]
                        elif src == '/'+portal_id:
                            src = '/'

                        # add . to have relative link to base href
                        if src[0] == '/':
                            src = '.' + src

                        img['src'] = urllib.quote(src)                        
                        LOG.info('rewrite_links: not convertible: %s'%src)


    def file_path(self, name):
        """ generate path to 'name' from 'destination' and context """
        if name:
            file_path = os.path.join(self.destination, self.path, name)
        else:
            file_path = os.path.join(self.destination, self.path)
        return file_path

    def save(self, name, data):
        """ save data on file system """
        path = self.file_path(name)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        try:
            f = open(path, 'w')
        except IOError:
            LOG.warning('IOError: %s'%path)
        else:
          f.write(str(data))
          f.close()

    def save_in_parent(self, name, data):
        """ save data on file system """
        file_path = os.path.join(self.destination, self.parent_path, name)
        f = open(file_path, 'w')
        f.write(str(data))
        f.close()

    def replace_base(self, html):
        """ replace base tag href attribute """
        base = html.find('base')
        base['href'] = self.static_base

    def add_html5manifest(self, html):
        """ add manifest to html """
        h = html.find('html')
        h['manifest'] = urlparse.urljoin(self.static_base , "resources.manifest")

    def index_html(self):
        """ Create index.html """
        html = self.render_page()
        self.save('index.html', html)
        self.manifest_data.add_entry('index.html', utilities.version(self.context))
        self.manifest_data.add_entry('', utilities.version(self.context), redirect='./index.html')

    def manifest(self):
        """ dump manifest.json file """
        self.save('manifest.json', self.manifest_data())

        # add to manifest-versions.json
        if hasattr(self.context, 'UID'):
            uid = self.context.UID()
        else:
            uid = 'root'
        data = {
          'title': self.context.Title(),
          'version': self.manifest_data.version,
          'url': self.file_path('manifest.json')[len(self.destination):],
        }

        self.transmogrifier.manifests[uid] = data

    def base_manifest_versions(self):
        """ save manifest-versions.json format """
        self.manifest_data.add_entry(
                              'manifest-versions.json',
                              utilities.version(self.context))

    def html5manifest(self):
        """ dump manifest.json file """
        self.save('resources.manifest', self.manifest_html5())

    def base_search_data(self):
        """ Initialize data used from offline search """
        catalog = getToolByName( self.portal, 'portal_catalog')
        brains = catalog(UID=self.context.UID())

        words = []
        for b in brains:
            rid = b.getRID()
            for w in catalog.getIndexDataForRID(rid)['SearchableText']:
                if w not in words:
                    words.append(w)

        words.sort() #sorting terms for a better search
        self.search_data = {
                'storeid': self.context.UID(),
                'contents': [{
                    'path': self.getRelativeContentPath(self.context),
                    'title': self.context.Title(),
                    'text': ' '.join(words),
                    }],
                }

    def save_search_data(self):
        """ save search_data in json format """
        for (name, adapter) in getAdapters((self,), ISearchDataDumper):
            adapter.dump()

    def add_page_html(self, context, dump_name = None, view = None):
        # add html page to dump
        LOG.info("-- %s of %s"%(dump_name, context.getId()))
        html = self.render_page(context, view)

        workflow = html.find(id='history')
        byline = html.find(id='plone-document-byline')

        if workflow is not None:
            workflow.extract()

        if byline is not None:
            byline.extract()

        dump_name = dump_name or context.id + '.html'
        self.save(dump_name, html)
        self.manifest_data.add_entry(dump_name, utilities.version(context))

    def dump(self):
        """ """
        raise NotImplemented

    def custom_dumps(self):
        """ """
        for (name, adapter) in getAdapters((self,), IExtensionDumper):
            adapter.dump()

    def update_manifest_with_files(self):
        """ """

        file_types = self.dumper.getDumperProperty('file_types', [])
        image_types = self.dumper.getDumperProperty('image_types', [])

        for item in self.context.objectValues():
            # check as config or marker interface...
            if item.Type() in file_types:
                self.manifest_data.add_entry(item.id, utilities.version(item))

            if item.Type() in image_types:
                for image in utilities.image_dump_name(item.id):
                    self.manifest_data.add_entry(image['name'], utilities.version(item))


# url rewriters
class BaseUrlRewriter(object):
    implements(IUrlRewriter)

    def __init__(self, context):
        self.context = context

    def rewrite_anchor(self, href):
        return href

class ContentUrlRewriter(BaseUrlRewriter):
    implements(IUrlRewriter)

    def rewrite_anchor(self, href):
        if not '.html' in href:
            href += '.html'
        return href


class FolderUrlRewriter(BaseUrlRewriter):
    implements(IUrlRewriter)

    def rewrite_anchor(self, href):
        return href + '/index.html'


class PloneSiteDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        LOG.info('site: %s'%self.context.id)
        self.index_html()
        self.base_search_data()
        self.custom_dumps()
        self.save_search_data()
        self.theme_elements()
        self.base_manifest_versions()
        self.manifest()
        self.html5manifest()

    def base_search_data(self):
        """ plone site specific data """
        self.search_data = {
                'storeid': 'root',
                'contents': [{
                    'path': '/',
                    'title': self.context.Title(),
                    'text': '',
                    }],
                }

    def theme_folders(self):
        folders = self.dumper.getDumperProperty('theme_folders', [])
        return [f for f in folders if f != '']

    def theme_elements(self):
        """ copy resources from template to destination, update manifest """
        if not os.path.exists(self.resources_destination):
            os.mkdir(self.resources_destination)

        for path in self.theme_folders():
            for id in os.listdir(path):
                if id != '.svn':
                    self.manifest_data.add_entry('resources_%s/%s'%(self.version, id), '')
                    self.manifest_html5.add_entry(id)
                    shutil.copyfile( \
                        os.path.join(path, id),
                        os.path.join(self.resources_destination, id))


class ImageDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        LOG.info('-- %s'%self.context.id)

        ddumper = queryAdapter(self.context, IDataDumper)
        if ddumper is not None:
            self.save('', ddumper.data())

        for image in utilities.image_dump_name(self.context.getId()):
            field = self.context.getField('image')
            scale = field.getScale(self.context, image['size'])
            if hasattr(scale, 'data'):
                self.save_in_parent(image['name'], scale.data)
            #XXX else?


class FileDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        LOG.info('-- %s'%self.context.id)
        ddumper = queryAdapter(self.context, IDataDumper)
        if ddumper is not None:
            self.save('', ddumper.data())
