from zope.event import notify
from zope.app.container.contained import ContainerModifiedEvent

from Acquisition import aq_parent
from DateTime import DateTime
from Products.Archetypes.event import ObjectEditedEvent


def updateParentModificationDate(obj, event):
    parent = aq_parent(obj)
    print "Modified date %s - %s" %(parent, event)
    parent.setModificationDate(obj.modified())
    
    if hasattr(parent, 'reindexObject'):
        parent.reindexObject(idxs=['ModificationDate'])
        
    notify(ObjectEditedEvent(parent))    


def updateModificationDate(obj, event):
    print "Modified date %s - %s" %(obj, event)

    obj.setModificationDate(DateTime())
    if hasattr(obj, 'reindexObject'):
        obj.reindexObject(idxs=['ModificationDate'])
        
    notify(ObjectEditedEvent(obj))
