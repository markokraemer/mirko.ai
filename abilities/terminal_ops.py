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
        """
        Run command in the terminal and wait for the result
        """
        result = self.container.exec_run(command)
        return OpsResult(
            ok=(result.exit_code == 0), output=result.output, exit_code=result.exit_code
        )

    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "name": TerminalOps.send_command.__name__,
                "description": TerminalOps.send_command.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to be executed in the terminal.",
                        }
                    },
                    "required": ["command"],
                },
            }
        ]
