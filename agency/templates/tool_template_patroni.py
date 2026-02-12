TOOL_TEMPLATE_PATRONI = """
class {class_name}:
    def run(self, executor):
        command = {command}
        return executor.run(command)
"""

