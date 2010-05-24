from Products.CMFCore.utils import getToolByName

def setupGroups(p):
    """
    Create Plone's default set of groups.
    """
    gtool = getToolByName(p, 'portal_groups')
    existing = gtool.listGroupIds()
    if 'Viewers' not in existing:
        gtool.addGroup('Viewers', roles=['Member', 'Dumper'])

def setupPlonePAS(context):
    if context.readDataFile('oops-staticdump.txt') is None:
        return
    site = context.getSite()
    setupGroups(site)
