Introduction
============

    Dumper and pipeline to generate PDF file from html page.
    The pipeline interacts with smartprintng server using a pdf converter
    based on pisa.


How to use
==========

    Add 'oops.dumpers.pdf' on the requirements section of at least one package
    (setup.py) or in the buildout.cfg file.

    In a package you must register the dumper for a content:

      <include package="oops.dumpers.pdf" />

      <adapter
          name="HTMLForPDFDumper"
          factory=".adapters.HTMLForPDFDumper"
          provides="oops.staticdump.dumpers.adapters.IDumper"
          for="collective.book.content.book.Book
               collective.transmogrifier.interfaces.ITransmogrifier"
          permission="zope.Public"
          />

    Remember to provide a browser view registered on the content named 'pdf_view'.

      <browser:page
          for="collective.book.interfaces.IBook"
          name="pdf_view"
          template="templates/bookpdfview.pt"
          permission="zope.Public"
          />

    Create a section in a transmogrifier configuration (dump.cfg):

      [transmogrifier]
      pipeline =
          ...
          pdfgenerator
          ...

      [pdfgenerator]
      blueprint = oops.pdfgenerator
      host = 127.0.0.1
      port = 6543

    where host and port are the parameters for the smartprintng.server
    and register the configuration in a zcml:

    <configure
        ...
        xmlns:transmogrifier="http://namespaces.plone.org/transmogrifier">
        ...

        <transmogrifier:registerConfig
          name="demo_dump"
          title="OOPS Demo site dump"
          configuration="dump.cfg"
          />
        ...

    Now you can create a dumper configuration in portal_dumper and use
    'demo_dump' as dump_configuration_name.

    See oops.demo.setup as example of configuration.

    You can register a specific pdf file name generator with:

            <adapter
              factory="my.content.MyContentPDFName"
              provides="opps.dumpers.pdf.interfaces.IPDFName"
              for="my.content.MyContent"
              permission="zope.Public"
              />

    then in your views you need to call the IPDFName adapter to generate the
    link to the file.


Tips and tricks

    Links to resources

      To generate the correct links you must use this zpt code:

          tal:define="base_url python:context.portal_dumper.getResourcesPath()"
          tal:attributes="src ${base_url}/logo.png"

      Or add a method to the associated browser view:

          @property
          def base_url(self):
              getToolByName(self.context, 'portal_dumper')
              return portal_dumper.getResourcesPath()