import os
import psycopg2
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

# Dossier contenant tous les fichiers HTML
DOC_DIR = "/var/lib/postgresql/documentationpg/admin"

# Connexion PostgreSQL
conn = psycopg2.connect(
    dbname="rag",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Charger le modèle d'embedding
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Chunking simple
def chunk_text(text, max_tokens=250):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_tokens
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        start = end

    return chunks

# Parcours des fichiers HTML
files = [f for f in os.listdir(DOC_DIR) if f.endswith(".html")]
print(f"Fichiers HTML trouvés : {len(files)}")

for filename in files:
    path = os.path.join(DOC_DIR, filename)

    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Toutes les sections possibles
    sections = soup.find_all(["div"], class_=["sect1", "sect2", "sect3"])

    print(f"{filename} → {len(sections)} sections")

    for sect in sections:
        title_tag = sect.find(["h1", "h2", "h3"])
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        html_id = sect.get("id", "unknown")

        content = sect.get_text(" ", strip=True)

        chunks = chunk_text(content, max_tokens=250)

        for i, chunk in enumerate(chunks):
            emb = model.encode(chunk).tolist()

            cur.execute("""
                INSERT INTO documents (content, embedding, metadata)
                VALUES (%s, %s, jsonb_build_object(
                    'title', %s,
                    'html_id', %s,
                    'file', %s,
                    'chunk_id', %s
                ));
            """, (chunk, emb, title, html_id, filename, i))

conn.commit()
cur.close()
conn.close()

print("Import complet terminé.")

