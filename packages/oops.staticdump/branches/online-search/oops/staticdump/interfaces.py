from zope.interface import Interface

class IDumper(Interface):

  def dump():
      """ Dump the content on file system: generate html, files and more """

class IExtensionDumper(Interface):

  def dump():
      """ called from Dumper implementations  """

class IExtensionRewriter(Interface):

  def rewrite_anchor(href):
      """ rewrite anchor """

# data dumpers
class IDataDumper(Interface):

  def data():
      """ Returns data to write on file system"""

class IAnnexesDataDumper(IDataDumper):
    """ Dump related annexes page """

class IPicturesDataDumper(IDataDumper):
    """ Dump related pictures page """
