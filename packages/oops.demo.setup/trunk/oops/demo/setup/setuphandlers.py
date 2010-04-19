import os
from oops.demo import setup as CURR_DIR

CONTENTS_TO_REMOVE = [
    'news',
    'events',
    'Members',
]

ZEXP_TO_IMPORT = [
    'book-1.zexp'
]

curr_dir = os.path.dirname(CURR_DIR.__file__)

def removePloneContents(context):
    if context.readDataFile('oops.demo.setup.setup_demo.txt') is None: return
    
    portal = context.getSite()
    
    for content_id in CONTENTS_TO_REMOVE:
        if content_id in portal.objectIds():
            portal._delObject(content_id)
            
            
def importDemoContents(context):
    if context.readDataFile('oops.demo.setup.setup_demo.txt') is None: return

    portal = context.getSite()
    
    for zexp in ZEXP_TO_IMPORT:
        try:
            portal._importObjectFromFile(os.path.join(curr_dir, zexp))
        except:
            pass
    
