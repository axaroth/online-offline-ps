from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.book import BookMessageFactory as _

class IChapter(Interface):
    """Contains Pages, images and files"""
    
    # -*- schema definition goes here -*-
