import os
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

# ============================
# 1. Charger la configuration
# ============================

load_dotenv()

BASE_DIR = os.getenv("DOC_DIR")  # ex: admin/
DB_NAME = os.getenv("DB_NAME", "rag")
DB_USER = os.getenv("DB_USER", "rag_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 250))

print("=== Configuration utilisée ===")
print(f"Dossier racine : {BASE_DIR}")
print(f"Base PostgreSQL : {DB_NAME}")
print(f"Utilisateur : {DB_USER}")
print(f"Chunk size : {CHUNK_SIZE}")
print("==============================")

# ============================
# 2. Connexion PostgreSQL
# ============================

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    print("Connexion PostgreSQL OK")
except Exception as e:
    print("Erreur de connexion PostgreSQL :", e)
    exit(1)

# ============================
# 3. Chunking
# ============================

def chunk_text(text, max_tokens=250):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_tokens
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        if chunk_text.strip():
            chunks.append(chunk_text)
        start = end

    return chunks

# ============================
# 4. Vérification du dossier racine
# ============================

if not BASE_DIR or not os.path.isdir(BASE_DIR):
    print(f"Erreur : dossier introuvable : {BASE_DIR}")
    conn.close()
    exit(1)

# ============================
# 5. Parcours multi-sources / versions
# ============================

for source in sorted(os.listdir(BASE_DIR)):
    source_path = os.path.join(BASE_DIR, source)
    if not os.path.isdir(source_path):
        continue

    for version in sorted(os.listdir(source_path)):
        version_path = os.path.join(source_path, version)
        if not os.path.isdir(version_path):
            continue

        print(f"\n=== Ingestion : {source} / {version} ===")

        html_files = [f for f in os.listdir(version_path) if f.endswith(".html")]
        print(f"Fichiers HTML trouvés : {len(html_files)}")

        for filename in tqdm(html_files, desc=f"{source}/{version}"):
            path = os.path.join(version_path, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
            except Exception as e:
                print(f"\nErreur lecture fichier {path} : {e}")
                continue

            # ============================
            # Sélection des sections selon la source
            # ============================

            if source == "postgresql":
                sections = soup.find_all("div", class_=["sect1", "sect2", "sect3"])
            elif source == "patroni":
                sections = soup.find_all("section")
            elif source == "pgbackrest":
                sections = soup.find_all("div", class_="section1")
            else:
                sections = soup.find_all("section")

            # ============================
            # Extraction et insertion
            # ============================

            for sect in sections:
                # Titre
                if source == "pgbackrest":
                    title_tag = sect.find("div", class_="section1-title")
                else:
                    title_tag = sect.find(["h1", "h2", "h3"])

                title = title_tag.get_text(strip=True) if title_tag else "Untitled"

                # ID HTML
                if source == "pgbackrest":
                    anchor = sect.find("a")
                    html_id = anchor.get("id", "unknown") if anchor else "unknown"
                else:
                    html_id = sect.get("id", "unknown")

                # Contenu
                if source == "pgbackrest":
                    body = sect.find("div", class_="section-body")
                    content = body.get_text(" ", strip=True) if body else ""
                else:
                    content = sect.get_text(" ", strip=True)

                if not content.strip():
                    continue

                chunks = chunk_text(content, max_tokens=CHUNK_SIZE)

                for i, chunk in enumerate(chunks):
                    # Vérifier si ce chunk existe déjà
                    cur.execute("""
                        SELECT 1
                        FROM documents
                        WHERE source = %s
                          AND version = %s
                          AND metadata->>'file' = %s
                          AND metadata->>'html_id' = %s
                          AND metadata->>'chunk_id' = %s;
                    """, (source, version, filename, html_id, str(i)))

                    exists = cur.fetchone()
                    if exists:
                        continue  # déjà ingéré

                    # Insertion sans embedding (NULL)
                    cur.execute("""
                        INSERT INTO documents (content, embedding, source, version, metadata)
                        VALUES (
                            %s,
                            NULL,
                            %s,
                            %s,
                            jsonb_build_object(
                                'title', %s,
                                'html_id', %s,
                                'file', %s,
                                'chunk_id', %s
                            )
                        );
                    """, (chunk, source, version, title, html_id, filename, i))

        conn.commit()

# ============================
# 6. Finalisation
# ============================

cur.close()
conn.close()

print("\nIngestion terminée (sans embeddings, prêts pour generate_embeddings.py).")

