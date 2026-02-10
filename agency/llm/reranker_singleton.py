import os
from sentence_transformers import CrossEncoder
import builtins

# Silence logs
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

if not hasattr(builtins, "_GLOBAL_RERANKER_MODEL"):
    builtins._GLOBAL_RERANKER_MODEL = None

def get_reranker_model():
    if builtins._GLOBAL_RERANKER_MODEL is None:
        builtins._GLOBAL_RERANKER_MODEL = CrossEncoder("BAAI/bge-reranker-large")
    return builtins._GLOBAL_RERANKER_MODEL

class RerankerSingleton:
    @classmethod
    def get_model(cls):
        return get_reranker_model()

