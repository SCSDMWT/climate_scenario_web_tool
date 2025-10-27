from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

class PostgresDB:
    def __init__(self):
        self.pool = None
        self.connection_url = ''

    def init_app(self, app):
        self.connection_url = app.config['DATABASE_URL']
        self.connect()

    def connect(self):
        self.pool = SimpleConnectionPool(1, 20, self.connection_url)
        return self.pool

    @contextmanager
    def get_cursor(self):
        if self.pool is None:
            self.connect()
        con = self.pool.getconn()
        try:
            yield con.cursor()
            con.commit()
        finally:
            self.pool.putconn(con)

pgdb = PostgresDB()
