import psycopg2
import psycopg2.extras
import os

class PostgresTool:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 5432)
        )
        self.conn.autocommit = True

    def query(self, sql, params=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows

    def get_roles(self):
        return self.query("SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin FROM pg_roles")

    def get_settings(self):
        return self.query("SELECT name, setting, unit, vartype, source FROM pg_settings")

    def get_activity(self):
        return self.query("""
            SELECT pid, usename, datname, state, wait_event, query
            FROM pg_stat_activity
            ORDER BY pid
        """)

    def get_replication_status(self):
        return self.query("""
            SELECT *
            FROM pg_stat_replication
        """)

    def get_locks(self):
        return self.query("""
            SELECT locktype, mode, granted, pid, relation::regclass
            FROM pg_locks
        """)

    def get_wal_stats(self):
        return self.query("""
            SELECT *
            FROM pg_stat_wal
        """)
