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