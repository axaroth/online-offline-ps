OOPS - Online/Offline Publication System

  Overview

    OOPS is a modular system to make a static dump of a Plone site, the product
    is used to make the site available offline.

    OOPS is not a generic Plone deployment systems but it is specifically used
    for generation of manuals used on the fields from humanitarian agencies.

    To have the offline availability the system dump the Plone site in static
    html using a specific theme and adding to html pages the Google Gears
    javascript library.

    The contents are dumped through specific adapters. The architecture is
    simple and extensible: it is possible to register new dumpers for
    non-foreseen contents.

    The base system is a Plone site with collective.book, this module provides
    two content types: a book and a chapter, paragraphs are provided through the
    standard Page.

  Installation

    http://code.google.com/p/online-offline-ps/wiki/DemoInstall

  Note

    The editor widget (Kupu, TinyMCE) must be configured to generate link with
    resolveUid. This generate correct url for dumper code.

Software architecture

  Components

    - Plone site

        As base Content Management System. From here one creates contents and
        configure how the site is dumped.

    - collective.book

        Some content types to create a structure book-like, with only three
        levels: book, chapters, paragraphs.
        In the chapters it is possible to add files and images.

    - oops.staticdump

        This module provides the base dumpers. It rewrites the urls in the pages
        and create the manifests for the Gears code, saves the pages on the file
        system so can be served to an external web server as Apache.

    - oops.dumpers

        Addictional dumpers: they are a proof of concept to show how to extend
        the base dumpers.

    - oops.dumpers.book

        Dumpers for collective.book contents.

    - yourproject.dumptheme

        Is the theme with which the contents of Plones are dumped. The static
        offline version requires some attention and specific javascript code.

    - yourproject.setup

        It contains the base profile for create the Plone site and configure
        the dumper and the skin.

  oops.staticdump

      It is composed from Transmogrifier sections:
        - 'sitewalker' walks the Plone
          site and extracts the contents to be dumped.
        - 'treebuilder' filters out the contents not needed (for example the
          'private' ones)
        - 'dumper' adapts the contents and generate the html to be written on
          file system.

    Dumpers

        There are two types of dumpers: IDumper and  IExtensionDumper.
        IDumper is used as base then all the IExtensionDumper registered for
        a content are called. You can register more IExtensionDumper and the
        tipical use case is to dump secondary views, for example a html page
        containing the list of images present in the content.
