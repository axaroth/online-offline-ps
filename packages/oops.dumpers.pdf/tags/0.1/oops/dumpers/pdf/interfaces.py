from zope.interface import Interface

class IPDFName(Interface):
    """ PDF file name generator adapter for contents"""

    def name():
        """ return a filename for the content """