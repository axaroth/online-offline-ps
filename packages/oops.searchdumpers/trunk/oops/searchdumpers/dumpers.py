import simplejson as json

from oops.staticdump.interfaces import ISearchDataDumper
from oops.staticdump import utilities
from pysqlite2 import dbapi2 as sqlite3
from zope.interface import implements

class OnlineSearchDumper(object):
    implements(ISearchDataDumper)

    def __init__(self, dumper):
        self.dumper = dumper
        self.portal = self.dumper.context

    def dump(self):
        # get the configured db
        db_path = '/tmp/search.db'
        dumper_properties = getattr(self.portal.portal_properties, 
                                    'dumper_properties', None)
                                    
        if dumper_properties is not None:
            db_path = dumper_properties.getProperty('search_db_path', 
                                                    '/tmp/search.db')
        
        # db connection    
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # if the Resources table does not exists, create it
        has_resources_table = cursor.execute("""
            SELECT name FROM sqlite_master WHERE name='Resources'
        """).fetchone()
                
        if not has_resources_table:
            try:
                connection.execute("""
                    CREATE VIRTUAL TABLE Resources USING fts3(StoreId, Url,
                    Title, SearchableText, DocumentType)
                """)
            except sqlite3.OperationalError:
                # maybe fts3 extension is not available
                has_resources_table = False

        if not has_resources_table: return #something wrong here, continue ...
        
        # remove all entries of current store_id
        search_data = self.dumper.search_data
        store_id = search_data.get('storeid', None)

        if store_id is None: return #something wrong here, continue ...
        
        cursor.execute("""
            DELETE from Resources where StoreId = ? 
        """, (store_id,))    
        
        # load new data and commit
        row_id = cursor.execute("""
            SELECT max(rowid) from Resources
        """).fetchone()[0] or 0
        
        for data in search_data.get('contents', []):  
            row_id += 1  
            path = convertString(data.get('path', ''))
            title = convertString(data.get('title', ''))
            text = convertString(data.get('text', ''))
            document_type = convertString(data.get('document_type', ''))
            
            cursor.execute("""
                INSERT INTO Resources (rowid, StoreId, Url, Title,
                SearchableText, DocumentType) VALUES (?, ?, ?, ?, ?, ?)
            """, (row_id, store_id, path, title, text, document_type))

                
        connection.commit()           
    
def convertString(val):
    if type(val)==str:
        val = val.decode('utf-8')
    return val
    

class OfflineSearchDumper(object):
    implements(ISearchDataDumper)

    def __init__(self, dumper):
        self.dumper = dumper
        self.portal = self.dumper.context

    def dump(self):
        self.dumper.save(
            'searchabletext.json', json.dumps(self.dumper.search_data))
        self.dumper.manifest_data.add_entry(
            'searchabletext.json',  utilities.version(self.dumper.context))   
            
                 
