from dataclasses import dataclass
from abc import ABC, abstractmethod
import os
import json
import docker


from abilities import file_util

@dataclass
class OpsResult:
    ok: bool
    exit_code: int
    output: str


class Ops(ABC):
    @abstractmethod
    def schema(self) -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        pass
    def ok_response(self, data: dict) -> OpsResult:
        """
        Create an successfull OpsResult with data as the output json.
        """
        text = json.dumps(data, indent=2)
        return OpsResult(ok=True, exit_code=0, output=text)

class TerminalOps(Ops):
    def __init__(self, container_name: str):
        self.client = docker.from_env()
        self.container = self.client.containers.get(container_name)

    def send_command(self, command: str) -> OpsResult:
        """
        Run command in the terminal and wait for the result
        """
        result = self.container.exec_run(command)
        # Since output is decoded to string, commands with binary output will not work.
        return OpsResult(
            ok=(result.exit_code == 0),
            output=str(result.output),
            exit_code=result.exit_code
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

def get_container_merged_dir(container_name: str):
    """
    Lookup workspace dir of docker container.
    Has a fallback for OrbStack, there may be other possibilities.
    It's not clear if there's a reliable way to get this.
    """
    fallback = os.path.expanduser(f"~/OrbStack/docker/containers/{container_name}")
    client = docker.from_env()
    container = client.containers.get(container_name)
    container_info = container.attrs
    merged_dir = container_info['GraphDriver']['Data']['MergedDir']
    if os.path.exists(merged_dir):
        return merged_dir
    if os.path.exists(fallback):
        return fallback
    raise Exception(f"Cannot find {container_name} container workspace dir")

def _rindex(li, value):
    return len(li) - li[-1::-1].index(value) - 1

class RetrievalOps(Ops):
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    def get_file_tree(self, path: str, depth: int=1) -> OpsResult:
        """
        List path recursively with limited depth. Path is relative to current dir.
        """
        if not os.path.exists(self.base_path):
            return OpsResult(
                ok=False, output="Base path does not exist", exit_code=1
            )
        path_parts = path.split(os.sep)
        # Handling . and ~ to avoid touching things outside base_path.
        if "." in path_parts:
            remaining_path = path_parts[_rindex(path_parts, ".") + 1:]
            effective_path = os.path.join(self.base_path, *remaining_path)
        else:
            effective_path = os.path.relpath(path, start=self.base_path)
        if "~" in path:
            return OpsResult(
                ok=False, output="Path cannot contain ~", exit_code=1
            )
        # This will catch any remaining case that could get outside base_path
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(self.base_path):
            return OpsResult(
                ok=False, output="Path is not within the base path", exit_code=1
            )
        try:
            listed_paths = file_util.find_files(effective_path, depth)
            return self.ok_response({'paths': listed_paths})
        except Exception as e:
            return OpsResult(
                ok=False, output=str(e), exit_code=1
            )

    
    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "name": RetrievalOps.get_file_tree.__name__,
                "description": RetrievalOps.get_file_tree.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory to list relative to current",
                        },
                        "depth": {
                            "type": "number",
                            "description": "Depth limit, default 1",
                        }
                    },
                    "required": ["path"],
                },
            }
        ]
