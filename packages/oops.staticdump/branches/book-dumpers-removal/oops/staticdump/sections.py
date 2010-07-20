import os
import simplejson as json

from zope.component import queryMultiAdapter
from zope.interface import classProvides, implements

from collective.transmogrifier.interfaces import ISection, ISectionBlueprint

from oops.staticdump.utilities import renew_folder
from oops.staticdump.interfaces import IDumper


def destination(transmogrifier):
    return transmogrifier['transmogrifier'].get('destination', '/tmp/dump')

class TreeBuilderSection(object):
    """ Create a tree on file system equivalent to plone site.
        Filter out not specified content types
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

        self.destination = destination(transmogrifier)
        renew_folder(self.destination)

        types = options.get('types', [])
        self.types = [t for t in types.splitlines() if t!='']

    def __iter__(self):
        for item in self.previous:
            if item.get('_type', '') in self.types:
                path = item.get('_path')
                final_destination = os.path.join(self.destination, path)
                renew_folder(final_destination)

            yield item


class DumperSection(object):
    """ For each entry call IDumper adapter """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier
        self.transmogrifier.manifests = {}
        self.transmogrifier.folders = []
        self.transmogrifier.others = []
        self.transmogrifier.voices = []
        self.transmogrifier.files = []
        self.transmogrifier.anchored_pages = []
        self.portal = transmogrifier.context

        types = self.transmogrifier['treebuilder'].get('types', [])
        self.types = [t for t in types.splitlines() if t!='']


    def manifests(self):
        """ save the manifests file """
        file_path = self.transmogrifier['transmogrifier'].get('destination', '/tmp/dump')
        f = open(os.path.join(file_path, 'manifest-versions.json'), 'w')
        f.write(json.dumps(self.transmogrifier.manifests))  # to check format
        f.close()

    def __iter__(self):
        for item in self.previous:
            if item.get('_type', '') in self.types:
                path = item.get('_path')
                obj = self.portal.restrictedTraverse(path)
                dumper = queryMultiAdapter((obj, self.transmogrifier), IDumper)
                if dumper is not None:
                    dumper.dump()

                yield item
        self.manifests()
