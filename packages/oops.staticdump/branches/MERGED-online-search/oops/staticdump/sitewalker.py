from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint

from Products.CMFCore.interfaces import IFolderish
from Products.Archetypes.interfaces import IBaseFolder

from Products.CMFCore.utils import getToolByName
from oops.staticdump.utilities import version, Filter

class SiteWalkerSection(object):
    """ walk the site, returns folder with his contents """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = options.get('path-key', '_path').strip()
        self.typekey = options.get('type-key', '_type').strip()
        self.entrieskey = options.get('entries-key', '_entries').strip()

        self.filter = Filter(self.context)

    def walk(self, obj):
        if self.filter.is_public(obj) or obj.meta_type=='Plone Site':
            if IFolderish.providedBy(obj) or IBaseFolder.providedBy(obj):
                contained = [(k, v.getPortalTypeName()) for k, v in obj.contentItems()]
                yield obj, tuple(contained)
                for v in obj.contentValues():
                    for x in self.walk(v):
                        yield x
            else:
                yield obj, ()
        else:
            yield None, ()

    def __iter__(self):
        for item in self.previous:
            yield item

        for obj, contained in self.walk(self.context):
            if obj is not None:
                item = {
                    self.pathkey: '/'.join(obj.getPhysicalPath()[2:]),
                    self.typekey: obj.getPortalTypeName(),
                }
                if contained:
                    item[self.entrieskey] = contained

                yield item