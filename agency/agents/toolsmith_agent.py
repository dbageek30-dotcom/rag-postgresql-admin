import os
from agency.templates.tool_template import TOOL_TEMPLATE
from agency.rag.rag_query import rag_query
from agency.db.connection import get_connection
from agency.llm.ollama_client import OllamaClient


class ToolsmithAgent:
    def __init__(self, rag_client=None, llm_client=None):
        """
        Agent chargé de générer dynamiquement des tools PostgreSQL
        à partir de la documentation officielle (via RAG) et d'un LLM distant (Ollama).
        """

        # RAG (local)
        self.rag = rag_client or rag_query

        # Modèle du Toolsmith = modèle par défaut défini dans .env
        default_model = os.getenv("OLLAMA_MODEL_DEFAULT")

        # Client LLM distant (7B par défaut)
        self.llm = llm_client or OllamaClient(model=default_model)

    # ----------------------------------------------------------------------
    # 1. Génération de tools pour les vues PostgreSQL
    # ----------------------------------------------------------------------
    def generate_tool_for_view(self, view_name: str, version: str, conn=None):
        if conn is None:
            conn = get_connection()

        # 1. Colonnes depuis la doc (RAG + LLM)
        doc_cols = self._get_columns_from_doc(view_name, version)

        # 2. Colonnes réelles depuis la base
        db_cols = self._get_columns_from_db(conn, view_name)

        # 3. Intersection doc ∩ DB
        final_cols = [c for c in doc_cols if c in db_cols]

        # 4. Fallback si le RAG/LLM ne renvoie rien
        if not final_cols:
            final_cols = db_cols

        # 5. Génération du code du tool
        class_name = f"{view_name.title().replace('_', '')}Tool"
        columns_str = ", ".join(final_cols)

        tool_code = TOOL_TEMPLATE.format(
            class_name=class_name,
            columns=columns_str,
            view_name=view_name,
        )

        return {
            "class_name": class_name,
            "columns": final_cols,
            "code": tool_code,
        }

    # ----------------------------------------------------------------------
    # 2. Extraction des colonnes depuis la documentation
    # ----------------------------------------------------------------------
    def _get_columns_from_doc(self, view_name: str, version: str):
        question = (
            f"List all column names of the PostgreSQL system view {view_name} "
            f"for PostgreSQL version {version}. "
            f"Answer with a plain list of column names, one per line."
        )

        rag_result = self.rag(question, source="postgresql", version=version)
        raw_text = "\n".join(r["content"] for r in rag_result["results"])

        if not raw_text.strip():
            return []

        prompt = f"""
Here is documentation text about the PostgreSQL view {view_name}:

{raw_text}

Extract ONLY the column names of this view.
Output one column name per line, no explanation.
"""

        llm_output = self.llm.chat(
            system_prompt="You extract column names from documentation.",
            user_prompt=prompt
        )

        cols = []
        for line in llm_output.splitlines():
            line = line.strip()
            if line:
                cols.append(line)

        return cols

    # ----------------------------------------------------------------------
    # 3. Extraction des colonnes depuis la base
    # ----------------------------------------------------------------------
    def _get_columns_from_db(self, conn, view_name: str):
        cur = conn.cursor()
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
            """,
            (view_name,),
        )
        rows = cur.fetchall()
        cur.close()
        return [r[0] for r in rows]

    # ----------------------------------------------------------------------
    # 4. Génération d’un tool SQL dynamique
    # ----------------------------------------------------------------------
    def generate_tool_for_command(self, sql_query: str):
        class_name = "PostgreSQLDynamicQueryTool"

        code = f"""
class {class_name}:
    \"""
    Tool PostgreSQL dynamique généré automatiquement.
    Exécute une requête SQL arbitraire.
    \"""

    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def run(self, args=None):
        import psycopg2
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(\"\"\"{sql_query}\"\"\")
        try:
            rows = cur.fetchall()
        except:
            rows = []
        conn.commit()
        cur.close()
        conn.close()

        return {{
            "query": \"\"\"{sql_query}\"\"\",
            "rows": rows
        }}
"""

        return {
            "class_name": class_name,
            "code": code
        }

