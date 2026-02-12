TOOL_TEMPLATE_PATRONI = """
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

