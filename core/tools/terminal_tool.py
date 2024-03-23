import docker
from .base import Tool, ToolResult
from ..utils.workspace_utils import get_docker_container_id

class TerminalTool(Tool):
    def __init__(self): #container_id: str
        self.client = docker.from_env()
        container_id = get_docker_container_id("workspace_dev-env_1") # Hard coded Docker Image Name
        if container_id is None:
            raise ValueError("No running container found for the standard docker image.")
        self.container = self.client.containers.get(container_id)

    def send_command(self, command: str) -> ToolResult:
        result = self.container.exec_run(command)
        return ToolResult(
            success=(result.exit_code == 0),
            output=str(result.output),
            exit_code=result.exit_code,
        )

    @staticmethod
    def schema() -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": TerminalTool.send_command.__name__,
                    "description": TerminalTool.send_command.__doc__,
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
                },
            }
        ]