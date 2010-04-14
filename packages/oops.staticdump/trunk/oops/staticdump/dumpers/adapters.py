import os, shutil
import simplejson as json

from zope.interface import directlyProvides, directlyProvidedBy
from zope.interface import Interface, implements, alsoProvides
from zope.component.interface import searchInterface
from zope.component import queryUtility
from zope.publisher.interfaces.browser import IBrowserSkinType

from Products.CMFCore.utils import getToolByName
from zope.component import queryAdapter, getAdapters

from BeautifulSoup import BeautifulSoup
from oops.staticdump.interfaces import IDumper, IDataDumper, IExtensionDumper, IExtensionRewriter

from oops import staticdump
from oops.staticdump import utilities

IMAGE_SIZES = ['large', 'preview', 'mini', 'thumb', 'tile', 'icon', 'listing']


class Manifest(object):

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


#
class BaseDumper(object):

    implements(IDumper)

    def __init__(self, context, transmogrifier):
        self.context = context
        self.transmogrifier = transmogrifier
        self.destination = transmogrifier['transmogrifier'].get('destination', '/tmp/dump')
        self.static_base = transmogrifier['transmogrifier'].get('static_base')
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.path = '/'.join(self.context.getPhysicalPath()[2:]) # remove portal id
        try:
            self.parent_path = '/'.join(self.context.aq_parent.getPhysicalPath()[2:])
        except:
            self.parent_path = ''
        self.manifest_data = Manifest()
        self.theme = self.portal.portal_properties.dumper_properties.getProperty('theme')
        self.search_data = {}


    def render_page(self, context=None, view=None):

        if context is None:
            context = self.context

        if view is None:
            view = context.getDefaultPage()

        request = getattr(self.portal.getPhysicalRoot(), 'REQUEST', None)

        # current skin
        current_skin = self.portal.getCurrentSkinName()
        current_skin_iface = queryUtility(IBrowserSkinType, name=current_skin)

        # dump skin
        dump_skin_iface = queryUtility(IBrowserSkinType, name=self.theme)

        # switch skin and layer
        self.portal.changeSkin(self.theme, request)
        if dump_skin_iface is not None:
            directlyProvides(request, dump_skin_iface +
                                      directlyProvidedBy(request) -
                                      current_skin_iface)

        if view is not None:
            sm = utilities.ReplaceSecurityManager(context, context.unrestrictedTraverse)
            data = sm.doItAs(utilities.USER, view)()
        else:
            sm = utilities.ReplaceSecurityManager(context, context.__call__)
            data = sm.doItAs(utilities.USER)

        # restore skin and layer
        self.portal.changeSkin(current_skin, request)
        if dump_skin_iface is not None:
            directlyProvides(request, current_skin_iface +
                                      directlyProvidedBy(request) -
                                      dump_skin_iface)

        html = BeautifulSoup(data.encode('utf-8', 'ignore'))
        self.replace_base(html)
        self.rewrite_links(html, context)

        return html

    def getRelativeContentPath(self, content):
        portal_url = self.portal.portal_url
        path = '/'+'/'.join(portal_url.getRelativeContentPath(content))
        if content.meta_type in ['Book', 'Chapter']:  # isfolderish?
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
        for anchor in html.findAll(['a', 'link']):
            href = anchor.get('href')
            #print '<<<',href
            if href is not None:

                # rewrite internal anchors in order to be absolute
                if href.startswith('#'):
                    href = context.absolute_url() + href

                # remove portal url
                href = href.replace(portal_url, '/'+portal_id)

                # add index.html in path relative to folders
                #if portal_id in href:
                if href.startswith('/'):
                    #print '===', href
                    try:
                        # remove internal anchor
                        if '#' in href:
                            href, sharp = href.split('#')
                        else:
                            sharp = ''

                        obj = self.portal.unrestrictedTraverse(
                                                    str(href).lstrip('/'), None)

                        if obj and hasattr(obj, 'UID'):
                            if obj.meta_type in ['Book', 'Chapter']:  # isfolderish?
                                self.transmogrifier.folders.append(obj.UID())
                            elif obj.meta_type in ['Voice',]:
                                self.transmogrifier.voices.append(obj.UID())
                            elif obj.meta_type in ['ATFile', 'ATImage']:
                                self.transmogrifier.files.append(obj.UID())
                            elif obj.meta_type in ['ATDocument',] \
                              and obj.aq_parent.meta_type=='Chapter':
                                self.transmogrifier.anchored_pages.append(obj.UID())
                            else:
                                self.transmogrifier.others.append(obj.UID())

                            if obj.UID() in self.transmogrifier.folders:
                                href += '/index.html'
                            elif obj.UID() in self.transmogrifier.others:
                                href += '.html'
                            elif obj.UID() in self.transmogrifier.files:
                                pass
                            elif obj.UID() in self.transmogrifier.anchored_pages:
                                parts = obj.aq_parent.getPhysicalPath()
                                href = '%s/index.html#%s' %('/'.join(parts), obj.getId())
                            elif obj.UID() in self.transmogrifier.voices:
                                # transform link to the voice content in anchors
                                # to the glossary view
                                parts = href.split('/')
                                href = '%s/index.html#%s' %('/'.join(parts[:-1]), parts[-1])

                        elif obj and getattr(obj, 'meta_type', None) == 'Plone Site':
                            href += '/index.html'

                        # and add again internal anchor
                        if sharp:
                            href += '#%s'%sharp

                    except Exception, e:
                        print e


                # remove portal id
                if portal_id == href[1:len(portal_id)+1]:
                    href = href[len(portal_id)+1:]

                href = self.custom_rewrite_anchor(href)

                # add . to have relative link to base href
                if href.startswith('/'):
                    href = '.' + href


                anchor['href'] = href
            #print '>>>', href

        # images
        for img in html.findAll('img'):
            src = img.get('src')
            if src is not None:
   
                obj = utilities.is_object_in(self.portal, src)
                if obj is None:
                    #second try, maybe it's relative path
                    fullpath = context.absolute_url()+'/'+src
                    obj = utilities.is_object_in(self.portal, fullpath)
                    if obj is not None:
                        src = fullpath

                if obj is not None:
                    # remove portal url
                    src = src.replace(portal_url, '')
                                        
                    # replace size
                    name, size = utilities.image_name_size_from(src)
                    size_value = utilities.size_value_of(size)
                    if size_value is not None:
                        new_name =  utilities.new_name(src)
                        old_name = '/%s/%s'%(name, size)
                        src = src.replace(old_name, new_name)

                    # remove portal id
                    if src.startswith('/' + portal_id):
                        src = src[len('/'+portal_id):]

                    # add . to have relative link to base href
                    if src[0] == '/':
                        src = '.' + src

                    img['src'] = src


    def file_path(self, name):
        """ generate path to 'name' from 'destination' and context """
        if name:
            file_path = os.path.join(self.destination, self.path, name)
        else:
            file_path = os.path.join(self.destination, self.path)
        return file_path

    def save(self, name, data):
        """ save data on file system """
        f = open(self.file_path(name), 'w')
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

    def index_html(self):
        """ Create index.html """
        html = self.render_page()
        self.save('index.html', html)
        self.manifest_data.add_entry('index.html', utilities.version(self.context))

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
        self.save('searchabletext.json', json.dumps(self.search_data))
        self.manifest_data.add_entry(
                              'searchabletext.json',
                              utilities.version(self.context))

    def add_page_html(self, context, dump_name = None, view = None):
        # add html page to dump
        print "-- %s of %s"%(dump_name, context.getId())
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

    def custom_rewrite_anchor(self, href):
        """ """
        for (name, adapter) in getAdapters((self,), IExtensionRewriter):
            href = adapter.rewrite_anchor(href)
        return href

    def update_manifest_with_files(self):
        """ """
        for item in self.context.objectValues():
            # check as config or marker interface...
            if item.Type() in ['File']:  
                self.manifest_data.add_entry(item.id, utilities.version(item))
            if item.Type() in ['Image']:
                for image in utilities.image_dump_name(item.id):
                    self.manifest_data.add_entry(image['name'], utilities.version(item))


#FIXME: must the a portal configuration
from ertoolkit import dumptheme
PATH = os.path.join(os.path.dirname(dumptheme.__file__), 'skins')

class PloneSiteDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        print 'site: ', self.context.id
        self.index_html()
        self.base_search_data()
        self.custom_dumps()
        self.save_search_data()
        self.theme_elements()
        self.base_manifest_versions()
        self.manifest()

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
        folders = self.portal.portal_properties.dumper_properties.getProperty('theme_folders', [])
        return [f for f in folders if f != '']

    def theme_elements(self):
        """ copy resources from template to destination, update manifest """
        for name in self.theme_folders():
            path = os.path.join(PATH, name)
            for id in os.listdir(path):
                if id != '.svn':
                    self.manifest_data.add_entry(id, '') # what for file system?
                    shutil.copyfile( \
                        os.path.join(path, id),
                        os.path.join(self.destination, id))


class BookDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        print 'book toc: ', self.context.id
        self.index_html()
        self.base_search_data()
        self.custom_dumps()
        self.save_search_data()
        self.manifest()


class ChapterDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        print 'chapter: ', self.context.id
        self.index_html()
        self.base_search_data()
        self.custom_dumps()
        self.update_manifest_with_files()
        self.save_search_data()
        self.manifest()

    def base_search_data(self):
        """ Get data from Documents and Files """
        catalog = getToolByName( self.portal, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())

        documents = catalog(
                        path=path,
                        meta_type="ATDocument")
        words = []
        for b in documents:
            rid = b.getRID()
            for w in catalog.getIndexDataForRID(rid)['SearchableText']:
                if w not in words:
                    words.append(w)

        self.search_data = {'storeid': self.context.UID(),
                'contents': [{
                    'path': self.getRelativeContentPath(self.context),
                    'title': self.context.Title(),
                    'text': ' '.join(words),
                    }],
                }

        # add files to 'contents'
        for item in catalog(path=path, meta_type="ATFile"):
            # check as config or marker interface...
            words = []
            rid = item.getRID()
            for w in catalog.getIndexDataForRID(rid)['SearchableText']:
                if w not in words:
                    words.append(w)

            self.search_data['contents'].append({
                'path': self.getRelativeContentPath(item.getObject()),
                'title': item.Title,
                'text': ' '.join(words),
            })


class ImageDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        print '--', self.context.id

        ddumper = queryAdapter(self.context, IDataDumper)
        if ddumper is not None:
            self.save('', ddumper.data())

        #head, ext =  os.path.splitext(self.context.getId())            
        #for size_value in IMAGE_SIZES:
        #    size_name = '%s_%s%s'%(head, size_value, ext)
        #    field = self.context.getField('image')
        #    scale = field.getScale(self.context, size_value)
        #    self.save_in_parent(size_name, scale.data)            
        
        for image in utilities.image_dump_name(self.context.getId()):
            field = self.context.getField('image')
            scale = field.getScale(self.context, image['size'])
            self.save_in_parent(image['name'], scale.data)            
        

class FileDumper(BaseDumper):

    implements(IDumper)

    def dump(self):
        """ """
        print '--', self.context.id
        ddumper = queryAdapter(self.context, IDataDumper)
        if ddumper is not None:
            self.save('', ddumper.data())


class GlossaryDumper(BaseDumper):

    implements(IDumper)


    def dump(self):
        """ """
        print 'glossary:', self.context.id
        self.index_html()
        self.custom_dumps()
        self.update_manifest_with_voices()
        self.manifest()

    def update_manifest_with_voices(self):
        """ """
        for item in self.context.objectValues():
            # check as config or marker interface...
            if item.Type() in ['Voice', ]:
                self.manifest_data.add_entry(item.id, utilities.version(item))
