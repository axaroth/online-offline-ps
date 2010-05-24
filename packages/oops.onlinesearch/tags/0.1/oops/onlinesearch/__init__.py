import simplejson

from pysqlite2 import dbapi2 as sqlite3
from paste.request import parse_formvars


class OOPSOnlineSearch(object):

    def __init__(self, database_path):
        self.database_path = database_path
    
    def __call__(self, environ, start_response):
        search_term = parse_formvars(environ).get('SearchTerm')
        document_type = parse_formvars(environ).get('document_type', None)
        response = {"results": []}
        
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()

        start_response('200 OK', [('content-type', 'application/json')])
        
        # check if Resources table exists or exit
        has_resources_table = cursor.execute("""
            SELECT name FROM sqlite_master WHERE name='Resources'
        """).fetchone()        
        
        if not has_resources_table: return simplejson.dumps(response)
        
        # do query
        if document_type is not None:
            results = cursor.execute("""
                SELECT Url, Title, DocumentType FROM Resources WHERE
                SearchableText MATCH ?
            """, (search_term,)).fetchall()
        else:
            results = cursor.execute("""
                SELECT Url, Title, DocumentType FROM Resources WHERE
                SearchableText MATCH ? and DocumentType = ?
            """, (search_term, document_type)).fetchall()
        
        # return results in json format
        for i in results:
            response['results'].append({
               'title': i[1], 
               'path': i[0],
               'document_type': i[2],
            })
        
        return simplejson.dumps(response)  


def app_factory(global_config, **local_conf):
    return OOPSOnlineSearch(local_conf.get('database_path'))
    
