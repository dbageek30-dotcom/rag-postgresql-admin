#!/usr/bin/env bash
set -e

BASE_DIR="agency"

echo "📁 Création de l'arborescence..."

mkdir -p $BASE_DIR/{llm,grammar,analyzer,planner,toolsmith,workers,executors,memory,orchestrator}

# ---------- llm_manager.py ----------
cat > $BASE_DIR/llm/llm_manager.py << 'PYEOF'
"""
LLM Manager
-----------
Rôle :
- Comprendre l'intention humaine
- Reformuler en intention structurée
- Ne PAS générer de syntaxe Patroni
- Ne PAS générer de commandes
"""

class LLMManager:
    def __init__(self, llm_client):
        self.llm = llm_client

    def interpret(self, user_input: str, cluster_state: dict) -> dict:
        """
        Retourne une intention structurée :
        {
            "action": "restart",
            "target": "replica",
            "selection": "most_lagged",
            "constraints": ["safe_only"]
        }
        """
        # TODO: prompt système + extraction d'intention
        raise NotImplementedError
PYEOF

# ---------- llm_reasoner.py ----------
cat > $BASE_DIR/llm/llm_reasoner.py << 'PYEOF'
"""
LLM Reasoner
------------
Rôle :
- Raisonnement complexe
- Explications
- Analyse métier
- Pas de syntaxe CLI
"""

class LLMReasoner:
    def __init__(self, llm_client):
        self.llm = llm_client

    def explain(self, plan: dict, cluster_state: dict) -> str:
        """
        Explique pourquoi le plan est correct ou risqué.
        """
        # TODO: prompt d'explication
        raise NotImplementedError
PYEOF

# ---------- patroni_extractor.py ----------
cat > $BASE_DIR/grammar/patroni_extractor.py << 'PYEOF'
"""
Patroni Grammar Extractor
-------------------------
Rôle :
- Exécuter `patronictl --help`
- Exécuter `patronictl <cmd> --help`
- Extraire la grammaire CLI
- Générer patroni_grammar.json
"""

class PatroniGrammarExtractor:
    def __init__(self, patroni_bin="/usr/bin/patronictl"):
        self.bin = patroni_bin

    def extract(self) -> dict:
        """
        Retourne une grammaire complète :
        {
            "list": {
                "positional_args": [...],
                "flags": {...}
            },
            ...
        }
        """
        # TODO: extraction CLI
        raise NotImplementedError
PYEOF

# ---------- grammar_loader.py ----------
cat > $BASE_DIR/grammar/grammar_loader.py << 'PYEOF'
"""
Grammar Loader
--------------
Charge la grammaire CLI depuis JSON.
"""

import json

class GrammarLoader:
    def __init__(self, path="patroni_grammar.json"):
        self.path = path

    def load(self) -> dict:
        with open(self.path) as f:
            return json.load(f)
PYEOF

# ---------- patroni_analyzer.py ----------
cat > $BASE_DIR/analyzer/patroni_analyzer.py << 'PYEOF'
"""
Patroni Analyzer
----------------
Rôle :
- Collecter l'état du cluster
- Analyser lag, roles, sync, health
- Fournir un état structuré
"""

class PatroniAnalyzer:
    def __init__(self, worker):
        self.worker = worker

    def get_cluster_state(self) -> dict:
        """
        Retourne :
        {
            "leader": "...",
            "replicas": [...],
            "health": "...",
            "lag": {...}
        }
        """
        # TODO: patronictl list + query + history
        raise NotImplementedError
PYEOF

# ---------- postgres_analyzer.py ----------
cat > $BASE_DIR/analyzer/postgres_analyzer.py << 'PYEOF'
"""
PostgreSQL Analyzer
-------------------
Rôle :
- Interroger les vues système PostgreSQL
- Fournir des métriques utiles au Reasoner
"""

class PostgresAnalyzer:
    def __init__(self, conn_params: dict):
        self.conn_params = conn_params

    def get_activity(self) -> dict:
        # TODO: pg_stat_activity
        raise NotImplementedError

    def get_replication_stats(self) -> dict:
        # TODO: pg_stat_replication
        raise NotImplementedError
PYEOF

# ---------- patroni_reasoner.py ----------
cat > $BASE_DIR/planner/patroni_reasoner.py << 'PYEOF'
"""
Patroni Reasoner
----------------
Rôle :
- Prendre une intention + état du cluster
- Décider quoi faire
- Générer un plan d'action
"""

class PatroniReasoner:
    def __init__(self, grammar: dict):
        self.grammar = grammar

    def plan(self, intention: dict, cluster_state: dict) -> dict:
        """
        Retourne un plan :
        {
            "command": "restart",
            "positional_args": ["pgcluster"],
            "flags": {"--member": "node3"}
        }
        """
        # TODO: logique métier
        raise NotImplementedError
PYEOF

# ---------- patroni_toolsmith.py ----------
cat > $BASE_DIR/toolsmith/patroni_toolsmith.py << 'PYEOF'
"""
Patroni Toolsmith
-----------------
Rôle :
- Transformer un plan en AST
- Compiler l'AST en commande CLI
- Générer un tool Python
"""

class PatroniToolsmith:
    def __init__(self, grammar: dict):
        self.grammar = grammar

    def to_ast(self, plan: dict) -> dict:
        # TODO: transformer plan → AST
        raise NotImplementedError

    def compile(self, ast: dict) -> str:
        # TODO: AST → commande CLI
        raise NotImplementedError

    def generate_tool(self, ast: dict) -> str:
        # TODO: template tool Python
        raise NotImplementedError
PYEOF

# ---------- tool_template.py ----------
cat > $BASE_DIR/toolsmith/tool_template.py << 'PYEOF'
"""
Tool Template
-------------
Template générique pour générer un tool Python exécutant une commande Patroni via SSH.
"""

TOOL_TEMPLATE = """
class {class_name}:
    def run(self, payload):
        from agency.executors.ssh_executor import SSHExecutor

        executor = SSHExecutor(
            host=payload["ssh_host"],
            user=payload["ssh_user"],
            ssh_key=payload["ssh_key"]
        )

        command = {command}
        return executor.run(command)
"""
PYEOF

# ---------- patroni_worker.py ----------
cat > $BASE_DIR/workers/patroni_worker.py << 'PYEOF'
"""
Patroni Worker
--------------
Rôle :
- Exécuter une commande via SSH
- Retourner stdout/stderr/exit_code
"""

class PatroniWorker:
    def __init__(self, executor):
        self.executor = executor

    def execute(self, command: str) -> dict:
        return self.executor.run(command)
PYEOF

# ---------- local_worker.py ----------
cat > $BASE_DIR/workers/local_worker.py << 'PYEOF'
"""
Local Worker
------------
Rôle :
- Exécuter une commande localement (optionnel)
"""

import subprocess

class LocalWorker:
    def execute(self, command: str) -> dict:
        # TODO: exécution locale sécurisée
        raise NotImplementedError
PYEOF

# ---------- ssh_executor.py ----------
# Si tu as déjà un fichier, ce bloc ne l'écrasera pas (on teste avant)
if [ ! -f $BASE_DIR/executors/ssh_executor.py ]; then
cat > $BASE_DIR/executors/ssh_executor.py << 'PYEOF'
"""
SSH Executor
------------
Rôle :
- Se connecter en SSH
- Exécuter une commande
- Retourner stdout/stderr/exit_code
"""

import paramiko
import traceback

class SSHExecutor:
    def __init__(self, host: str, user: str, ssh_key: str):
        self.host = host
        self.user = user
        self.ssh_key = ssh_key

    def run(self, command: str) -> dict:
        # TODO: implémentation (tu as déjà une version fonctionnelle)
        raise NotImplementedError
PYEOF
fi

# ---------- incident_memory.py ----------
cat > $BASE_DIR/memory/incident_memory.py << 'PYEOF'
"""
Incident Memory
---------------
Rôle :
- Stocker incidents
- Détecter patterns
"""

class IncidentMemory:
    def record(self, event: dict):
        # TODO
        raise NotImplementedError

    def search(self, query: str) -> list:
        # TODO
        raise NotImplementedError
PYEOF

# ---------- knowledge_graph.py ----------
cat > $BASE_DIR/memory/knowledge_graph.py << 'PYEOF'
"""
Knowledge Graph
---------------
Rôle :
- Relier événements, nœuds, incidents
"""

class KnowledgeGraph:
    def add_relation(self, source: str, target: str, relation: str):
        # TODO
        raise NotImplementedError

    def query(self, pattern: dict) -> list:
        # TODO
        raise NotImplementedError
PYEOF

# ---------- orchestrator.py ----------
cat > $BASE_DIR/orchestrator/orchestrator.py << 'PYEOF'
"""
Orchestrator
------------
Pipeline complet :
- intention → analyse → plan → AST → commande → exécution
"""

class Orchestrator:
    def __init__(self, manager, analyzer, reasoner, toolsmith, worker):
        self.manager = manager
        self.analyzer = analyzer
        self.reasoner = reasoner
        self.toolsmith = toolsmith
        self.worker = worker

    def run(self, user_input: str):
        cluster_state = self.analyzer.get_cluster_state()
        intention = self.manager.interpret(user_input, cluster_state)
        plan = self.reasoner.plan(intention, cluster_state)
        ast = self.toolsmith.to_ast(plan)
        command = self.toolsmith.compile(ast)
        result = self.worker.execute(command)
        return result
PYEOF

echo "✅ Arborescence et squelette créés."
