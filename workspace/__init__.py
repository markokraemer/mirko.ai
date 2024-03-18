# __init__.py

import docker
from dataclasses import dataclass

@dataclass
class OpsResult:
    ok: bool
    exit_code: int
    output: bytes


class TerminalOps:
    def __init__(self, container_name: str):
        self.client = docker.from_env()
        self.container = self.client.containers.get(container_name)

    def send_command(self, command: str) -> OpsResult:
        result = self.container.exec_run(command)
        return OpsResult(
            ok=(result.exit_code==0),
            output=result.output,
            exit_code=result.exit_code
        )
    @staticmethod
    def schema() -> dict:
        """
        Returns the JSON schema for a function call.
        """
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to be executed in the terminal."
                }
            },
            "required": ["command"]
        }
def smoke_test():
    print(TerminalOps("workspace-dev-env-1").send_command("ls"))
    print(TerminalOps.schema())

smoke_test()