import sys
this_module = sys.modules[ __name__ ]
staticdump_globals = globals()

def initialize(context):

    import dumpertool
    from Products.CMFPlone.utils import ToolInit

    ToolInit('Static Dumper Tool'
             , tools=[dumpertool.DumperTool,]
             , icon='tool.png'
             ).initialize( context )
             
             
## OOPS LOGGER
import logging
logger = logging.getLogger('oops.staticdump')

logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('/tmp/oops.log')
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)                 
