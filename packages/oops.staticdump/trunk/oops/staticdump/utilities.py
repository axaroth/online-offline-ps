import os
import re
import shutil
import urlparse
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
        if '' not in self.states:
            self.states.append('')
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

def parse_size(size):
    if size != '':
        elements = size.split('_')
        name = '_'.join(elements[:-1])
        value = elements[-1]
        return (name, value)
    else:
        return None

def new_name(src):
    name, size = image_name_size_from(src)
    size_value = size_value_of(size)
    head, ext =  os.path.splitext(name)
    return '/%s_%s%s'%(head, size_value, ext)

def image_dimensions(obj, field_name, size_value):
    # obj is Products.Archetypes.Field.Image: size is the real one
    try:
        return obj.getField(field_name).getSize(obj.aq_parent, size_value)
    except:
        return (0, 0)

#
def path_from(url):
    # remove protocol and host if present
    path = urlparse.urlparse(url)[2]
    query = urlparse.urlparse(url)[4]
    if path.startswith('/'):
        path = path[1:]
    if query:
        return str('%s?%s'%(path, query))
    else:
        return str(path)

def is_external(context, url):
    # check if url is external
    netloc = urlparse.urlparse(url)[1]
    if netloc in context.absolute_url():
        return False
    else:
        return True

def is_object_in(context, src):
    """
      Try to recover the object with src url/path in the context.
      src can be a path or a url
      src must be just checked with is_external
    """
    url_tool = context.portal_url
    portal_url = url_tool()
    src = str(src)
    
    if src.startswith(portal_url):
        src = src.replace(portal_url, '')

    if src.startswith('..'):
        result = context.unrestrictedTraverse(src, None)
        if result is not None:
            return result

    if not src in ['', '#']:
        # remove virtual url based on context (due to rewriting rules)
        src = src.replace(url_tool.getPortalObject().absolute_url_path(), '')
        object_found = context.unrestrictedTraverse("%s%s" %(url_tool.getPortalPath(), src), None)
        if object_found is None:
            # finally try to get the file from the url as is, otherwise return None
            return context.unrestrictedTraverse(src, None)
    
    return None
    
#
def external_url(context, obj=None):
    """ To use in the skins for external urls based on html_base"""
    html_base = getToolByName(context, 'portal_dumper').getDumperProperty('html_base')
    if obj is None:
          return html_base
    else:
        portal = getToolByName(context, 'portal_url').getPortalObject()
        obj_path = obj.absolute_url(1).replace(portal.id, '')
        while obj_path[0] == '/':
              obj_path = obj_path[1:]
        path = "%s/%s"%(html_base, obj_path)
        return path

