import os
from sentence_transformers import SentenceTransformer

# Désactiver les logs AVANT tout import HF
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class EmbeddingSingleton:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        return cls._model

