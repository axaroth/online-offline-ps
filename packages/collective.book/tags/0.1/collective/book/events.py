from Acquisition import aq_parent
from DateTime import DateTime

def updateParent(obj, event):
    parent = aq_parent(obj)
    parent.setModificationDate(obj.modified())
    if hasattr(parent, 'reindexObject'):
        parent.reindexObject(idxs=['ModificationDate'])

def updateChapter(obj, event):
    obj.setModificationDate(DateTime())
    if hasattr(obj, 'reindexObject'):
        obj.reindexObject(idxs=['ModificationDate'])
