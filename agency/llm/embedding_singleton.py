import os
from sentence_transformers import SentenceTransformer

# Désactiver les logs HF
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Registre global partagé entre TOUS les modules Python
import builtins

if not hasattr(builtins, "_GLOBAL_EMBEDDING_MODEL"):
    builtins._GLOBAL_EMBEDDING_MODEL = None


def get_embedding_model():
    if builtins._GLOBAL_EMBEDDING_MODEL is None:
        builtins._GLOBAL_EMBEDDING_MODEL = SentenceTransformer("BAAI/bge-base-en-v1.5")
    return builtins._GLOBAL_EMBEDDING_MODEL


class EmbeddingSingleton:
    @classmethod
    def get_model(cls):
        return get_embedding_model()

