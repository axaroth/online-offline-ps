from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from interfaces import IDumpStartedEvent, IDumpCompletedEvent


class DumpStartedEvent(ObjectEvent):
    """The dump has been started"""
    implements(IDumpStartedEvent)


class DumpCompletedEvent(ObjectEvent):
    """The dump has been completed"""
    implements(IDumpCompletedEvent)
