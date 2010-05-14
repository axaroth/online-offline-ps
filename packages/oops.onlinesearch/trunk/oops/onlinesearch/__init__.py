import simplejson

from pysqlite2 import dbapi2 as sqlite3
from paste.request import parse_formvars


class OOPSOnlineSearch(object):

    def __init__(self, database_path):
        connection = sqlite3.connect(database_path)
        self.cursor = connection.cursor()        
    
    def __call__(self, environ, start_response):
        start_response('200 OK', [('content-type', 'application/json')])
        search_term = parse_formvars(environ).get('SearchTerm')

        #self.cursor.execute('SELECT Url, Title, DocumentType FROM Resources WHERE SearchableText MATCH ? and DocumentType = ?')
        response = {
            "results": [
              {'title': 'A first result %s' %search_term, 
               'path': '/somewhere/index.html',
               'document_type': 'Page'},
              {'title': 'A second result %s' %search_term, 
               'path': '/nowhere.zip',
               'document_type': 'File'},
            ] 
        }
        
        return simplejson.dumps(response)  

def app_factory(global_config, **local_conf):
    return OOPSOnlineSearch(local_conf.get('database_path'))
