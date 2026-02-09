import os
from sentence_transformers import SentenceTransformer

# Désactiver les logs AVANT tout import HF
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Variable globale au module (vraiment unique)
_GLOBAL_EMBEDDING_MODEL = None

def get_embedding_model():
    global _GLOBAL_EMBEDDING_MODEL
    if _GLOBAL_EMBEDDING_MODEL is None:
        _GLOBAL_EMBEDDING_MODEL = SentenceTransformer("BAAI/bge-base-en-v1.5")
    return _GLOBAL_EMBEDDING_MODEL


class EmbeddingSingleton:
    @classmethod
    def get_model(cls):
        return get_embedding_model()

