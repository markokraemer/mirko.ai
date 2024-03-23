import os
from .base import Tool, ToolResult
from ..utils.file_utils import find_files
# from core.utils.workspace_utils import get_working_dir_path # didnt work, hard coded for now

def _rindex(li, value):
    return len(li) - li[-1::-1].index(value) - 1


class RetrievalTool(Tool):
    def __init__(self):
        self.base_path = "/root/softgen.ai/mirko.ai/working_directory" # Hard coded for now
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

    def get_file_tree(self, path: str, depth: int = 1) -> ToolResult:
        """
        List path recursively with limited depth. Path is relative to current dir.
        """
        if not os.path.exists(self.base_path):
            return self.fail_response("Base path does not exist")

        if "~" in path:
            return self.fail_response("Path cannot contain ~")
        effective_path = self._get_effective_path(path)
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            return ToolResult(
                success=False, output="Path is not within the base path", exit_code=1
            )
        try:
            listed_paths = find_files(effective_path, depth)
            return self.success_response({"paths": listed_paths})
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)

    def read_file_contents(self, path: str) -> ToolResult:
        """
        Show the contents of the file at path relative to current dir
        """
        if not os.path.exists(self.base_path):
            return self.fail_response("Base path does not exist")
        effective_path = self._get_effective_path(path)
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            return ToolResult(
                success=False, output="Path is not within the base path", exit_code=1
            )
        if os.path.exists(effective_path):
            with open(effective_path, "r") as file:
                text = file.read()
            return self.success_response(text)
        else:
            return self.fail_response("File does not exist")

    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": RetrievalTool.get_file_tree.__name__,
                    "description": RetrievalTool.get_file_tree.__doc__,
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
                    "name": RetrievalTool.read_file_contents.__name__,
                    "description": RetrievalTool.read_file_contents.__doc__,
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


if __name__ == "__main__":
    tool = RetrievalTool()
    # Sample usage of get_file_tree
    print("Getting file tree:")
    file_tree_result = tool.get_file_tree("", 2)
    print(file_tree_result.output)

    # Sample usage of read_file_contents
    print("\nReading file contents:")
    file_contents_result = tool.read_file_contents("file1.py")
    print(file_contents_result.output)
