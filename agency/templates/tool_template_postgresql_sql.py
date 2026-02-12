TOOL_TEMPLATE_POSTGRESQL_SQL = """
class {class_name}:
    \"""
    Tool PostgreSQL SQL généré dynamiquement.
    Utilise la connexion SQL fournie par le worker.
    \"""

    def __init__(self, conn=None, **params):
        self.conn = conn
        self.params = params

    def run(self):
        from psycopg2.extras import RealDictCursor

        if self.conn is None:
            return {{"status": "error", "message": "Aucune connexion SQL fournie au tool."}}

        query = {command_repr}

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                if cur.description:
                    return cur.fetchall()
                return {{"status": "success", "rows": cur.rowcount}}
        except Exception as e:
            return {{"status": "error", "message": str(e)}}
"""

