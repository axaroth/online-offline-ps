import simplejson as json

from Products.CMFCore.utils import getToolByName

from oops.staticdump.interfaces import ISearchDataDumper, IExtensionDumper
from oops.staticdump import utilities
from pysqlite2 import dbapi2 as sqlite3
from zope.interface import implements

from logging import getLogger
LOG = getLogger('oops.searchdumpers')

class BaseSearchDumper(object):

    def __init__(self, dumper):
        self.dumper = dumper
        self.portal = self.dumper.context

    def db_path(self):
        # get the configured db
        dumper_tool = getToolByName(self.portal, 'portal_dumper')
        db_path = dumper_tool.getDumperProperty('search_db_path', '')
        return db_path


class OnlineSearchDumper(BaseSearchDumper):
    """ Create and fill the Resources table """

    implements(ISearchDataDumper)

    def dump(self):
        """ """
        db_path = self.db_path()
        if db_path:
            LOG.info('onlinesearch: Resources update')
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
                except sqlite3.OperationalError, e:
                    # maybe fts3 extension is not available
                    if 'no such module: fts3' == str(e):
                        LOG.info('onlinesearch: fts3 module not available')
                    else:
                        LOG.info('onlinesearch: %s'%str(e))
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
        else:
            LOG.info('onlinesearch: db_path not defined')


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
        """ """
        LOG.info('offlinesearch: json data')
        self.dumper.save(
            'searchabletext.json', json.dumps(self.dumper.search_data))
        self.dumper.manifest_data.add_entry(
            'searchabletext.json',  utilities.version(self.dumper.context))


class CleanOnlineSearchDumper(BaseSearchDumper):
    """ Remove the Resources table """

    implements(IExtensionDumper)

    def dump(self):
        """ """
        db_path = self.db_path()
        if db_path:
            LOG.info('clean: remove Resources Table')

            # db connection
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            # if the Resources table exists, drop it
            has_resources_table = cursor.execute("""
                SELECT name FROM sqlite_master WHERE name='Resources'
            """).fetchone()

            if has_resources_table:
                connection.execute("""
                    DROP TABLE Resources
                """)

            connection.commit()
        else:
            LOG.info('clean: db_path not defined')
