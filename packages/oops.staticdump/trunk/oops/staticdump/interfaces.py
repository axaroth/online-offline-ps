from zope.interface import Interface

class IDumper(Interface):

  def dump():
      """ Dump the content on file system: generate html, files and more """

class IExtensionDumper(Interface):

  def dump():
      """ called from Dumper implementations  """

class ISearchDataDumper(IDumper):
    """ Dumper related to search data """

class IUrlRewriter(Interface):

  def rewrite_anchor(href):
      """ rewrite anchor """

# data dumpers
class IDataDumper(Interface):

  def data():
      """ Returns data to write on file system"""

# language dumpers
class ILanguageDumper(Interface):

  def i18n_language():
      """ Returns the language code to be used during the dump """

# events
from zope.component.interfaces import IObjectEvent

class IDumpStartedEvent(IObjectEvent):
    """The dump has been started"""

class IDumpCompletedEvent(IObjectEvent):
    """The dump has been completed"""

class IBeforeDumpSwitchEvent(IObjectEvent):
    """Contents have been dumped"""
    
    
