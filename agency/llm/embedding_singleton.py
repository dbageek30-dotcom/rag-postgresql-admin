import os
import logging
from sentence_transformers import SentenceTransformer
import builtins

# Désactiver tous les logs HF / Transformers / tqdm
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tqdm").setLevel(logging.ERROR)

# Registre global partagé
if not hasattr(builtins, "_GLOBAL_EMBEDDING_MODEL"):
    builtins._GLOBAL_EMBEDDING_MODEL = None


def get_embedding_model():
    if builtins._GLOBAL_EMBEDDING_MODEL is None:
        model = SentenceTransformer(
            "BAAI/bge-base-en-v1.5",
            device="cpu",
            trust_remote_code=True
        )

        # Désactiver tqdm au niveau du modèle
        if hasattr(model, "progress_bar"):
            model.progress_bar = False

        builtins._GLOBAL_EMBEDDING_MODEL = model

    return builtins._GLOBAL_EMBEDDING_MODEL


class EmbeddingSingleton:
    @classmethod
    def get_model(cls):
        return get_embedding_model()

