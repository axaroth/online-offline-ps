from oops.staticdump import utilities
from oops.staticdump.dumpers.adapters import BaseDumper, ImageDumper, \
                                             FileDumper, BaseUrlRewriter
from oops.staticdump.templates.adapters import BaseDataDumper, ImageDataDumper,\
                                               FileDataDumper 
from oops.staticdump.interfaces import IDumper, IDataDumper, IUrlRewriter
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

# Book
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


class BookDataDumper(BaseDataDumper):
    implements(IDataDumper)
    

# Chapter    
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
                        meta_type="Paragraph")
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
        for item in catalog(path=path, meta_type="FileAnnex"):
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


class ChapterDataDumper(BaseDataDumper):
    implements(IDataDumper)


# Paragraph
class ParagraphUrlRewriter(BaseUrlRewriter):
    """ rewite the link to the chapter with an anchor """
    implements(IUrlRewriter)

    def rewrite_anchor(self, href):
        parts = self.context.aq_parent.getPhysicalPath()
        return '%s/index.html#%s' %('/'.join(parts), self.context.getId())

# Voice
class VoiceUrlRewriter(BaseUrlRewriter):
    """ rewite the link to the glossary with an anchor """
    implements(IUrlRewriter)

    def rewrite_anchor(self, href):
        parts = self.context.aq_parent.getPhysicalPath()
        return '%s/index.html#%s' %('/'.join(parts), self.context.getId())


# ImageAnnex
class ImageAnnexDumper(ImageDumper):
    implements(IDumper)


class ImageAnnexDataDumper(ImageDataDumper):
    implements(IDataDumper)


# FileAnnex        
class FileAnnexDumper(FileDumper):
    implements(IDumper)


class FileAnnexDataDumper(FileDataDumper):
    implements(IDataDumper)


# Glossary
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
                
                
class GlossaryDataDumper(BaseDataDumper):
    implements(IDataDumper)
