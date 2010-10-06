import os
import re
import shutil
from Products.CMFCore.utils import getToolByName

#
from AccessControl import ClassSecurityInfo, getSecurityManager, Unauthorized
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Products.CMFCore.utils import getToolByName

USER = {
    'uid':'viewer',
    'group':'Viewers',
    'roles':('Member', 'Dumper'),   # Dumper must have the cmf.ManagePortal
    }

class ReplaceSecurityManager:

    def __init__(self, context, do):
        self.do = do
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.members = self.portal.acl_users
        self.rtool = getToolByName(self.portal, 'portal_registration')

    def replaceSecurityManager(self, member_id):
        """ """
        member = self.members.getUserById(member_id)
        assert member, "There's no user with id %r" % member_id
        if not hasattr(member, 'aq_base'):
            member = member.__of__(members)
        old_sec_manager = getSecurityManager()
        newSecurityManager(None, member)
        return old_sec_manager

    def createUser(self, user):
        upwd = self.rtool.getPassword(20)
        self.members.userFolderAddUser(user['uid'], upwd, user['roles'], (), (user['group'],))

    def exists_user(self, uid):
        return self.members.getUserById(uid)

    def doItAs(self, user, *args):
        """ """
        if not self.exists_user(user['uid']):
            self.createUser(user)

        old_security_manager = self.replaceSecurityManager(user['uid'])
        results = ''
        try:
            results = self.do(*args)
        finally:
            setSecurityManager(old_security_manager)

        return results

#
def renew_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.mkdir(path)


def version(context):
    """ formats the modified date """
    return context.modified().strftime('%Y-%m-%d %H:%M')


class Filter(object):

    def __init__(self, portal):
        pp = getToolByName(portal, 'portal_properties')
        self.states = list(pp.navtree_properties.getProperty('wf_states_to_show', []))
        self.wf = getToolByName(portal, 'portal_workflow')

    def is_public(self, content):
        return self.wf.getInfoFor(content, 'review_state', '') in self.states

    def public_contents(self, contents):
        return [o for o in contents if self.is_public(o)]

# images
def image_name_size_from(src):
    # src is in the form: http://host:port/f1/f2/img.png/image_size
    # image can have any extension
    m = re.compile('.*/(.*)/(image_.*)')
    res = m.match(src)
    if res is not None:
        name, size = res.groups()
        return (name, size)
    else:
        return  ('', '')

def image_dump_name(id):
    values = []
    head, ext =  os.path.splitext(id)
    for size_value in ['large', 'preview', 'mini', 'thumb', 'tile', 'icon', 'listing']:
        size_name = '%s_%s%s'%(head, size_value, ext)
        values.append({
            'size' : size_value,
            'name' : size_name,
        })
    return values

def size_value_of(size):
    if size != '':
        return size.split('_')[-1]
    else:
        return None

def new_name(src):
    name, size = image_name_size_from(src)
    size_value = size_value_of(size)
    head, ext =  os.path.splitext(name)
    return '/%s_%s%s'%(head, size_value, ext)

def path_from(src):
    # src is url to image
    if 'http' in src:
        return str('/'.join(src.split('/')[3:]))
    else:
        if src.startswith('/'):
            src = src[1:]
        return str(src)

def is_object_in(portal, src):
    return portal.unrestrictedTraverse(path_from(src), None)
