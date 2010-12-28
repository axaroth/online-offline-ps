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
