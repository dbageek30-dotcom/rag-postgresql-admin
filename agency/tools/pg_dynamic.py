from .rag import rag_query
from .db import conn

class DynamicPostgresTool:
    def __init__(self, version):
        self.version = version
        self.conn = conn

    def get_columns_from_doc(self, view_name):
        q = f"List all columns of the PostgreSQL view {view_name} for version {self.version}"
        result = rag_query(q, source="postgresql", version=self.version)
        cols = []
        for r in result["results"]:
            for line in r["content"].splitlines():
                if "-" in line and ":" in line:
                    col = line.split("-")[0].strip()
                    cols.append(col)
        return cols

    def get_columns_from_db(self, view_name):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
        """, (view_name,))
        rows = cur.fetchall()
        cur.close()
        return [r[0] for r in rows]

    def resolve_columns(self, view_name):
        doc_cols = self.get_columns_from_doc(view_name)
        db_cols = self.get_columns_from_db(view_name)
        return [c for c in doc_cols if c in db_cols]

    def select(self, view_name):
        cols = self.resolve_columns(view_name)
        if not cols:
            return {"error": f"No matching columns for {view_name}"}

        sql = f"SELECT {', '.join(cols)} FROM {view_name} LIMIT 50"
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()

        return {"view": view_name, "columns": cols, "rows": rows}

