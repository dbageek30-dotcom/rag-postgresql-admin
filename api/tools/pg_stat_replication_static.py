# api/tools/pg_stat_replication_static.py

class PgStatReplicationTool:
    def __init__(self, conn):
        self.conn = conn

    def run(self, limit=50):
        sql = """
            SELECT pid,
                   usesysid,
                   usename,
                   application_name,
                   client_addr,
                   state,
                   sent_lsn,
                   write_lsn,
                   flush_lsn,
                   replay_lsn,
                   write_lag,
                   flush_lag,
                   replay_lag
            FROM pg_stat_replication
            LIMIT %s
        """
        cur = self.conn.cursor()
        cur.execute(sql, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows

