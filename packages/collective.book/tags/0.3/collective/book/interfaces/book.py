from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.book import BookMessageFactory as _

class IBook(Interface):
    """Contains Chapters"""
    
    # -*- schema definition goes here -*-
