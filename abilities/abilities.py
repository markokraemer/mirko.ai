from dataclasses import dataclass
from abc import ABC, abstractmethod
import os
import json
import docker
from pathlib import Path
from enum import Enum
from xml.dom.minidom import getDOMImplementation

from abilities import file_util

__XML_DOM__ = getDOMImplementation()

@dataclass
class OpsResult:
    ok: bool
    exit_code: int
    output: str


class Ops(ABC):
    @classmethod
    @abstractmethod
    def openai_schema() -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        pass

    @classmethod
    def anthropic_schema(cls) -> str:
        """
        Return Anthropic Claude tool definition XML as a string
        https://docs.anthropic.com/claude/docs/functions-external-tools
        """
        doc = __XML_DOM__.createDocument(None, "tools", None)
        for tool_dict in cls.openai_schema():
            desc_node = doc.createElement("tool_description")
            tool_name_node = doc.createElement("tool_name")
            tool_name_node.appendChild(doc.createTextNode(tool_dict['function']['name']))
            desc_node.appendChild(tool_name_node)

            description_node = doc.createElement("description")
            description_node.appendChild(doc.createTextNode(tool_dict['function']['description']))
            desc_node.appendChild(description_node)

            parameters_node = doc.createElement("parameters")
            for param_name, param in tool_dict['function']['parameters']['properties'].items():
                parameter_node = doc.createElement("parameter")

                name_node = doc.createElement("name")
                name_node.appendChild(doc.createTextNode(param_name))
                parameter_node.appendChild(name_node)

                type_node = doc.createElement("type")
                type_node.appendChild(doc.createTextNode(param['type']))
                parameter_node.appendChild(type_node)

                description_node = doc.createElement("description")
                description_node.appendChild(doc.createTextNode(param['description']))
                parameter_node.appendChild(description_node)

                parameters_node.appendChild(parameter_node)

            desc_node.appendChild(parameters_node)
            doc.documentElement.appendChild(desc_node)
        return doc.toxml()

    def ok_response(self, data: dict | str) -> OpsResult:
        """
        Create an successfull OpsResult with data as the output json.
        """
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, indent=2)
        return OpsResult(ok=True, exit_code=0, output=text)

    def fail_response(self, msg: str, code: int = 1) -> OpsResult:
        """
        Create an successfull OpsResult with data as the output json.
        """
        return OpsResult(ok=False, exit_code=code, output=msg)


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
            exit_code=result.exit_code,
        )

    @classmethod
    def openai_schema(cls) -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "type": "function",
                "function": {
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
    merged_dir = container_info["GraphDriver"]["Data"]["MergedDir"]
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
        # The docstrings are what the agent sees.
        # When they say relative to the current dir, that means be the current dir
        # in the container terminal session once we are wired up.

    def _get_effective_path(self, path: str) -> str:
        # Handling . and ~ to avoid touching things outside base_path.
        path_parts = path.split(os.sep)
        if "." in path_parts:
            remaining_path = path_parts[_rindex(path_parts, ".") + 1 :]
            effective_path = os.path.join(self.base_path, *remaining_path)
        else:
            effective_path = os.path.join(self.base_path, path)
        return effective_path

    def get_file_tree(self, path: str, depth: int = 1) -> OpsResult:
        """
        List path recursively with limited depth. Path is relative to current dir.
        """
        if not os.path.exists(self.base_path):
            return self.fail_response("Base path does not exist")

        if "~" in path:
            return self.fail_response("Path cannot contain ~")
        effective_path = self._get_effective_path(path)
        # This will catch any remaining case that could get outside base_path
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            return OpsResult(
                ok=False, output="Path is not within the base path", exit_code=1
            )
        try:
            listed_paths = file_util.find_files(effective_path, depth)
            return self.ok_response({"paths": listed_paths})
        except Exception as e:
            return OpsResult(ok=False, output=str(e), exit_code=1)

    def read_file_contents(self, path: str) -> OpsResult:
        """
        Show the contents of the file at path relative to current dir
        """
        if not os.path.exists(self.base_path):
            return self.fail_response("Base path does not exist")
        effective_path = self._get_effective_path(path)
        print(effective_path)
        # Make sure we didn't break out of base_path
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            return OpsResult(
                ok=False, output="Path is not within the base path", exit_code=1
            )
        if os.path.exists(effective_path):
            with open(effective_path, "r") as file:
                text = file.read()
            return self.ok_response(text)
        else:
            return self.fail_response("File does not exist")

    @classmethod
    def openai_schema(cls) -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "type": "function",
                "function": {
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
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": RetrievalOps.read_file_contents.__name__,
                    "description": RetrievalOps.read_file_contents.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of file relative to current dir",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
        ]
