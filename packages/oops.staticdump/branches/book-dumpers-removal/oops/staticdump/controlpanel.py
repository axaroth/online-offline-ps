import os
import shutil

from collective.transmogrifier.interfaces import ITransmogrifier

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.form import FieldsetsEditForm
from zope.app.component.hooks import getSite
from zope.formlib import form

from zope.interface import directlyProvides
from zope.interface import Interface
from zope.interface import implements

from zope.schema import Choice #TextLine
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

# fixme: remove old fields if no more needed

def DumpersVocabularyFactory(context):
    """Vocabulary factory for dumpers ids
    """
    portal = getSite()
    tool = getToolByName(portal, 'portal_dumper')
    terms = [SimpleTerm(o.getId(), title=o.title) for o in tool.objectValues()]
    return SimpleVocabulary(terms)

directlyProvides(DumpersVocabularyFactory, IVocabularyFactory)


class IDumpPanelSchema(Interface):

    dumper = Choice(
        title=u'Dumpers',
        description=u'Available dumpers',
        vocabulary=u'oops.staticdump.dumpers'
    )

    #filesystem_target = TextLine(
        #title=u'Filesystem target',
        #description=u"Path on server filesystem",
    #)

    #html_base = TextLine(
        #title=u'HTML base',
        #description=u"Base attribute value used in html files",
    #)


class DumpPanelAdapter(SchemaAdapterBase):

    implements(IDumpPanelSchema)

    def __init__(self, context):
        super(DumpPanelAdapter, self).__init__(context)
        self.portal = getSite()
        dumper_tool = getToolByName(self.portal, 'portal_dumper')
        self.context = dumper_tool

    dumper = ProxyFieldProperty(IDumpPanelSchema['dumper'])

    #filesystem_target = ProxyFieldProperty(IDumpPanelSchema['filesystem_target'])
    #html_base = ProxyFieldProperty(IDumpPanelSchema['html_base'])


class DumpPanel(ControlPanelForm):
    """A simple form to run the site dump."""

    implements(IDumpPanelSchema)

    form_fields = form.FormFields(IDumpPanelSchema)
    label = u'Static version'
    description = u"Update static version of this site"
    form_name = u'Dump'

    #def setUpWidgets(self, ignore_request=False):
        ## this is the only way to call the super methods
        #FieldsetsEditForm.setUpWidgets(self, ignore_request)
        ##self.widgets['filesystem_target'].displayWidth = 50
        ##self.widgets['html_base'].displayWidth = 50


    def __call__(self):
        self.update()

        portal = getSite()
        if dump_is() == running:
            if not 'Dump' in self.status:
                self.status =  '%s %s'%('Dump running.', self.status)
            else:
                self.status = 'Dump running.'

        return self.render()

    #def _applyChanges(self, data):
        ## save the base attribute always with an ending '/'
        #html_base = data.get('html_base', '')
        #if not html_base.endswith('/'):
            #data['html_base'] = html_base + '/'

        #form.applyChanges(self.context, self.form_fields, data, self.adapters)

    @form.action(u'Save', name=u'save')
    def handle_save(self, action, data):
        #self._applyChanges(data)
        tool = getToolByName(self.context, 'portal_dumper')
        tool.setDumper(data['dumper'])
        self.status = u'Save completed.'

    @form.action(u'Save and dump now', name=u'dump')
    def handle_dump(self, action, data):
        #self._applyChanges(data)
        tool = getToolByName(self.context, 'portal_dumper')
        tool.setDumper(data['dumper'])

        if dump_is() == running:
            self.status = 'Dump running.'
        else:
            dump_is(running)

            # do dump
            #destination = data.get('filesystem_target')
            destination = tool.getDumperProperty('filesystem_target')
            tmp = destination + '_tmp'

            transmogrifier_overrides = {
                'destination': tmp,
                #'static_base': data.get('html_base')
                'static_base':tool.getDumperProperty('html_base')
            }

            transmogrifier = ITransmogrifier(self.context)
            configuration_name = tool.getDumperProperty(
                                    'dump_configuration_name',
                                    'dump_sample')
            try:
                transmogrifier(configuration_name,
                               transmogrifier = transmogrifier_overrides)
            except:
                dump_is(not_running)
                raise

            backup_and_switch(destination, tmp)
            dump_is(not_running)
            self.status = u'Dump completed.'


def backup_and_switch(destination, tmp):
    if os.path.exists(destination):
        old = destination + '_old'
        if os.path.exists(old):
            shutil.rmtree(old)
        shutil.move(destination, old)
        shutil.move(tmp, destination)


running = True
not_running = False
def dump_is(status=None):
    portal = getSite()
    tool = getToolByName(portal, 'portal_dumper')
    return tool.status(status)