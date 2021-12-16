from sqlalchemy import create_engine
import logging


class PostgreSQLClient:
    def __init__(self, host, port, user, password, database):
        port = int(port)
        uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri, echo=False)
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_last_ad(self) -> dict:
        sql = 'SELECT * FROM ads ORDER BY index DESC LIMIT 1'

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchone()

    def find_chats_by_ad(self, ad):
        where = []
        if ad['price']:
            where.append('(price_max IS NULL OR price_max >= %d)' % ad['price'])
        if ad['size']:
            where.append('(size_min IS NULL OR size_min >= %d)' % ad['size'])
        if ad['rooms']:
            where.append('(rooms_min IS NULL OR rooms_min <= %d)' % ad['rooms'])

        if len(where) == 0:
            self.logger.warning('No features for filtering. Skipping ad: %s' % str(ad))
            return []

        sql = '' \
              'SELECT chat_id ' \
              'FROM search_requests ' \
              'WHERE ' + ' AND '.join(where)

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            for row in cursor.fetchall():
                yield row[0]

    def find_ads_since(self, index: int):
        sql = 'SELECT * FROM ads WHERE index > %d ORDER BY index ASC' % index

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()
