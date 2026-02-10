# agency/workers/patroni_worker.py

import subprocess

class PatroniWorker:
    def __init__(self, params):
        self.params = params

    def execute_tool(self, code: str, params: dict):
        namespace = {}
        exec(code, namespace)

        ToolClass = namespace["PatroniTool"]
        tool = ToolClass(
            patroni_bin=params.get("patroni_bin", "/usr/bin/patronictl"),
            config_file=params.get("patroni_config", "/etc/patroni.yml")
        )

        return tool.run()

