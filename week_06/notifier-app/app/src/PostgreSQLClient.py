from sqlalchemy import create_engine


class PostgreSQLClient:
    def __init__(self, host, port, user, password, database):
        port = int(port)
        uri = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri, echo=False)

    def find_last_ad(self) -> dict:
        sql = 'SELECT * FROM ads ORDER BY index DESC LIMIT 1'

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchone()

    def find_chats_by_ad(self, ad):
        sql = '' \
              'SELECT chat_id ' \
              'FROM search_requests ' \
              'WHERE ' \
              '(price_max IS NULL OR price_max >= %d) AND ' \
              '(size_min IS NULL OR size_min >= %d) AND ' \
              '(rooms_min IS NULL OR rooms_min <= %d)' % \
              (ad['price'], ad['size'], ad['rooms'])

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def find_ads_since(self, index: int):
        sql = 'SELECT * FROM ads WHERE index > %d ORDER BY index ASC' % index

        with self.engine.connect() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()
