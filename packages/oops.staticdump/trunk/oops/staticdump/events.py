from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from interfaces import IDumpStartedEvent, IDumpCompletedEvent, IBeforeDumpSwitchEvent


class DumpStartedEvent(ObjectEvent):
    """The dump has been started"""
    implements(IDumpStartedEvent)


class DumpCompletedEvent(ObjectEvent):
    """The dump has been completed"""
    implements(IDumpCompletedEvent)
    
    
class BeforeDumpSwitchEvent(ObjectEvent):
    """All contents dumped, perform actions before the switch"""
    implements(IBeforeDumpSwitchEvent)    
