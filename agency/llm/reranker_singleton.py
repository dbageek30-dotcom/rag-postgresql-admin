import os
import logging
from sentence_transformers import CrossEncoder
import builtins

# Désactiver tous les logs HF / Transformers / tqdm
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tqdm").setLevel(logging.ERROR)

# Registre global partagé
if not hasattr(builtins, "_GLOBAL_RERANKER_MODEL"):
    builtins._GLOBAL_RERANKER_MODEL = None


def get_reranker_model():
    if builtins._GLOBAL_RERANKER_MODEL is None:
        model = CrossEncoder(
            "BAAI/bge-reranker-large",
            device="cpu",
            trust_remote_code=True
        )

        # Désactiver tqdm si présent
        if hasattr(model, "progress_bar"):
            model.progress_bar = False

        builtins._GLOBAL_RERANKER_MODEL = model

    return builtins._GLOBAL_RERANKER_MODEL


class RerankerSingleton:
    @classmethod
    def get_model(cls):
        return get_reranker_model()

