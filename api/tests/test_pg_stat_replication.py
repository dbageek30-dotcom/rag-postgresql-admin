from api.db import get_connection
from api.tools.pg_stat_replication_static import PgStatReplicationTool

# 1. Connexion à PostgreSQL
conn = get_connection()

# 2. Instanciation du tool statique
tool = PgStatReplicationTool(conn)

# 3. Exécution du tool
rows = tool.run(limit=5)

# 4. Affichage du résultat
for row in rows:
    print(row)

