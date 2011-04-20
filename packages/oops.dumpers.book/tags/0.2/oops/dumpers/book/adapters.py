from oops.staticdump import utilities
from oops.staticdump.dumpers.adapters import BaseDumper, ImageDumper, \
                                             FileDumper, BaseUrlRewriter
from oops.staticdump.templates.adapters import BaseDataDumper, ImageDataDumper,\
                                               FileDataDumper 
from oops.staticdump.interfaces import IDumper, IDataDumper, IUrlRewriter, \
                                       IExtensionDumper 
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from logging import getLogger
LOG = getLogger('oops.dumpers.book')

# PloneSite
class PloneSiteExtensionDumper(object):
    """ Add annexes and pictures pages in the site root """
    implements(IExtensionDumper)

    def __init__(self, dumper):
        self.dumper = dumper
        self.context = self.dumper.context

    def dump(self):
        LOG.info('Site: %s'% self.context.id)
        self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'pictures.html',
                        view='pictures')
        self.dumper.add_page_html(
                        self.dumper.context,
                        dump_name = 'annexes.html',
                        view='annexes')


# Book
class BookDumper(BaseDumper):
    implements(IDumper)

    def dump(self):
        """ """
        LOG.info('Book: %s'% self.context.id)
        self.index_html()

        # add annexes and pictures pages
        self.add_page_html(self.context, dump_name = 'pictures.html',
                           view='pictures')
        self.add_page_html(self.context, dump_name = 'annexes.html',
                           view='annexes')

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
        LOG.info('Chapter: %s'% self.context.id)
        self.index_html()

        # add annexes and pictures pages
        self.add_page_html(self.context, dump_name = 'pictures.html',
                           view='pictures')
        self.add_page_html(self.context, dump_name = 'annexes.html',
                           view='annexes')


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
                        meta_type=["Paragraph", "Chapter"]) #add also the chapter

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

        # add files and images annexes to 'contents'
        for item in catalog(path=path, meta_type=["FileAnnex", "ImageAnnex"]):
            # check as config or marker interface...
            words = []
            rid = item.getRID()
            for w in catalog.getIndexDataForRID(rid)['SearchableText']:
                if w not in words:
                    words.append(w)

            obj = item.getObject()
            if obj.meta_type == 'FileAnnex':
                document_type = obj.getDocument_type()
            elif obj.meta_type == 'ImageAnnex':
                document_type = obj.getPicture_type()
            else:
                document_type = ''

            self.search_data['contents'].append({
                'path': self.getRelativeContentPath(item.getObject()),
                'title': item.Title,
                'text': ' '.join(words),
                'document_type': document_type,
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
        LOG.info('Glossary: %s'% self.context.id)
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
