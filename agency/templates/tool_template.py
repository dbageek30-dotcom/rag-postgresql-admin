TOOL_TEMPLATE = """
class {class_name}:
    def __init__(self, conn):
        self.conn = conn

    def run(self, limit=50):
        sql = "SELECT {columns} FROM {view_name} LIMIT %s"
        cur = self.conn.cursor()
        cur.execute(sql, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
"""

