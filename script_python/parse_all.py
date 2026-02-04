import os
import psycopg2
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

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

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 250))

print("=== Configuration utilisée ===")
print(f"Dossier racine : {BASE_DIR}")
print(f"Base PostgreSQL : {DB_NAME}")
print(f"Utilisateur : {DB_USER}")
print(f"Modèle : {MODEL_NAME}")
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
# 3. Charger le modèle
# ============================

print(f"Chargement du modèle : {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

# ============================
# 4. Chunking
# ============================

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

# ============================
# 5. Vérification du dossier racine
# ============================

if not BASE_DIR or not os.path.isdir(BASE_DIR):
    print(f"Erreur : dossier introuvable : {BASE_DIR}")
    exit(1)

# ============================
# 6. Parcours multi-sources
# ============================

for source in os.listdir(BASE_DIR):
    source_path = os.path.join(BASE_DIR, source)
    if not os.path.isdir(source_path):
        continue

    for version in os.listdir(source_path):
        version_path = os.path.join(source_path, version)
        if not os.path.isdir(version_path):
            continue

        print(f"\n=== Ingestion : {source} / {version} ===")

        html_files = [f for f in os.listdir(version_path) if f.endswith(".html")]
        print(f"Fichiers HTML trouvés : {len(html_files)}")

        for filename in html_files:
            path = os.path.join(version_path, filename)

            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # ============================
            # Sélection des sections selon la source
            # ============================

            if source == "postgresql":
                # HTML généré depuis AsciiDoc → div.sect1/2/3
                sections = soup.find_all("div", class_=["sect1", "sect2", "sect3"])

            elif source == "patroni":
                # HTML généré par Sphinx → <section>
                sections = soup.find_all("section")

            elif source == "pgbackrest":
                # Documentation HTML officielle pgBackRest → <div class="section1">
                sections = soup.find_all("div", class_="section1")

            else:
                # fallback générique
                sections = soup.find_all("section")

            print(f"{filename} → {len(sections)} sections")

            # ============================
            # Extraction et insertion
            # ============================

            for sect in sections:

                # Titre selon la source
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

                chunks = chunk_text(content, max_tokens=CHUNK_SIZE)

                for i, chunk in enumerate(chunks):
                    emb = model.encode(chunk).tolist()

                    cur.execute("""
                        INSERT INTO documents (content, embedding, source, version, metadata)
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            jsonb_build_object(
                                'title', %s,
                                'html_id', %s,
                                'file', %s,
                                'chunk_id', %s
                            )
                        );
                    """, (chunk, emb, source, version, title, html_id, filename, i))

# ============================
# 7. Finalisation
# ============================

conn.commit()
cur.close()
conn.close()

print("\nImport complet terminé.")

