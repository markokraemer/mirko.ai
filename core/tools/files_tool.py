import os
from .base import Tool, ToolResult
from ..utils.llm import make_llm_api_call
from ..utils.file_utils import find_files, EXCLUDED_FILES, EXCLUDED_EXT, _should_exclude




def _rindex(li, value):
    return len(li) - li[-1::-1].index(value) - 1

class FilesTool(Tool):
    def __init__(self):
        self.base_path = "/root/softgen.ai/mirko.ai/working_directory" # Hard coded for now

    def _get_effective_path(self, path: str) -> str:
        # Handling . and ~ to avoid touching things outside base_path.
        path_parts = path.split(os.sep)
        if "." in path_parts:
            remaining_path = path_parts[_rindex(path_parts, ".") + 1 :]
            effective_path = os.path.join(self.base_path, *remaining_path)
        else:
            effective_path = os.path.join(self.base_path, path)
        return effective_path


# <----> Specialised Actions

    def edit_file_contents(self, file_path: str, instructions: str) -> ToolResult:
        """
        Edit file contents based on instructions
        """
        effective_path = self._get_effective_path(file_path)
        if not os.path.exists(effective_path):
            return ToolResult(success=False, output=f"File {file_path} does not exist.", exit_code=1)
        try:
            with open(effective_path, 'r') as file:
                current_content = file.read()
            # Construct messages for LLM API call
            messages = [
                {
                    "role": "system",
                    "content": "You are a brilliant and meticulous engineer. When you write code, the code works on the first try, is syntactically perfect and is fully complete. You have the utmost care for the code that you write, so you do not make mistakes and every function and class is fully implemented. \n Under NO CIRCUMSTANCES should the file be stripped of the majority of contents, make deliberate changes instead. \n Make sure to output the complete newFileContents in the JSON property newFileContents, do not create additional properties – but Output the complete File Contents all within 'newFileContents'"
                },
                {"role": "user", "content": f"This is the current content of the file you are editing '{file_path}':\n\n<current_content>{current_content}</current_content> \nYou are now implement the following instructions for {file_path}: {instructions}\n.\n.Respond in this JSON Format, OUTPUT EVERYTHING IN FOLLOWING JSON PROPERTIES, do not add new properties but output in File, FileName, newFileContents. Make sure to ONLY EDIT {file_path}. Strictly respond in this JSON Format:\n\n {{\n  \"File\": {{\n    \"FilePath\": \"{file_path}\",\n    \"newFileContents\": \"The whole file contents, the complete code – The contents of the new file with all instructions implemented perfectly. NEVER write comments. Keep the complete File Contents within this single JSON Property.\"}}\n}}\n"}
            ]
            # Placeholder for make_llm_api_call function, which should be implemented
            response_json = make_llm_api_call(messages, "gpt-4-turbo-preview", json_mode=True, max_tokens=4096) 
            if not response_json or 'newFileContents' not in response_json:
                raise ValueError("Invalid response from LLM API call")
            new_content = response_json['newFileContents']
            with open(effective_path, 'w') as file:
                file.write(new_content)
            return self.success_response(f"File {file_path} edited successfully based on instructions")
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)

# <----> Basic File Ops

    def create_file(self, file_path: str) -> ToolResult:
        """
        Create a file at file_path, path is relative to current dir
        """
        effective_path = self._get_effective_path(file_path)
        if os.path.exists(effective_path):
            return self.fail_response("File already exists")
        try:
            open(effective_path, 'w').close()
            return self.success_response(f"File {file_path} created successfully")
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)

    def move_file(self, current_file_path: str, new_file_path: str) -> ToolResult:
        """
        Move a file from current_file_path to new_file_path, both paths are relative to current dir
        """
        current_effective_path = self._get_effective_path(current_file_path)
        new_effective_path = self._get_effective_path(new_file_path)
        if not os.path.exists(current_effective_path):
            return self.fail_response("Current file does not exist")
        try:
            os.rename(current_effective_path, new_effective_path)
            return self.success_response(f"File renamed from {current_file_path} to {new_file_path}")
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)

    def rename_file(self, old_file_path: str, new_file_path: str) -> ToolResult:
        """
        Rename a file from old_file_path to new_file_path, paths are relative to current dir
        """
        old_effective_path = self._get_effective_path(old_file_path)
        new_effective_path = self._get_effective_path(new_file_path)
        if not os.path.exists(old_effective_path):
            return self.fail_response("Old file does not exist")
        if os.path.exists(new_effective_path):
            return self.fail_response("New file name already exists")
        try:
            os.rename(old_effective_path, new_effective_path)
            return self.success_response(f"File renamed from {old_file_path} to {new_file_path}")
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)

    def delete_file(self, file_path: str) -> ToolResult:
        """
        Delete the file at file_path, path is relative to current dir
        """
        effective_path = self._get_effective_path(file_path)
        if not os.path.exists(effective_path):
            return self.fail_response("File does not exist")
        try:
            os.remove(effective_path)
            return self.success_response(f"File {file_path} deleted successfully")
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)


# <----> Retrieval

    def get_file_tree(self, path: str, depth: int = 3) -> ToolResult:
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

    def read_directory_contents(self, path: str) -> ToolResult:
        """
        List all files and directories at the given path, including their contents, excluding certain files and directories as specified in file_utils.py.
        """
        if not os.path.exists(self.base_path):
            return self.fail_response("Base path does not exist")
        effective_path = self._get_effective_path(path)
        if not os.path.exists(effective_path) or not os.path.isdir(effective_path):
            return self.fail_response("Directory does not exist or is not a directory")
        try:
            directory_contents = {}
            for root, dirs, files in os.walk(effective_path):
                # Apply exclusions for directories
                dirs[:] = [d for d in dirs if not _should_exclude(self.base_path, os.path.join(root, d))]
                # Apply exclusions for files
                files = [f for f in files if not _should_exclude(self.base_path, os.path.join(root, f)) and f not in EXCLUDED_FILES and not any(f.endswith(ext) for ext in EXCLUDED_EXT)]
                # Append relative paths of files and directories to contents and read file contents
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(file_path, effective_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file_content:
                            directory_contents[relative_file_path] = file_content.read()
                    except UnicodeDecodeError:
                        # Skip files that cannot be decoded with UTF-8
                        continue
            return self.success_response({"contents": directory_contents})
        except Exception as e:
            return ToolResult(success=False, output=str(e), exit_code=1)


    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the JSON schema for OpenAI function calls.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": FilesTool.edit_file_contents.__name__,
                    "description": FilesTool.edit_file_contents.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path of the file to edit, relative to current dir",
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Instructions on how to edit the file contents",
                            }
                        },
                        "required": ["file_path", "instructions"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.create_file.__name__,
                    "description": FilesTool.create_file.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path for the new file to create, relative to current dir",
                            }
                        },
                        "required": ["file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.move_file.__name__,
                    "description": FilesTool.move_file.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "current_file_path": {
                                "type": "string",
                                "description": "Current path of the file, relative to current dir",
                            },
                            "new_file_path": {
                                "type": "string",
                                "description": "New path for the file, relative to current dir",
                            }
                        },
                        "required": ["current_file_path", "new_file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.rename_file.__name__,
                    "description": FilesTool.rename_file.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "old_file_path": {
                                "type": "string",
                                "description": "Old path of the file, relative to current dir",
                            },
                            "new_file_path": {
                                "type": "string",
                                "description": "New path for the file, relative to current dir",
                            }
                        },
                        "required": ["old_file_path", "new_file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.delete_file.__name__,
                    "description": FilesTool.delete_file.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path of the file to delete, relative to current dir",
                            }
                        },
                        "required": ["file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.get_file_tree.__name__,
                    "description": FilesTool.get_file_tree.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory to list relative to current",
                            },
                            "depth": {
                                "type": "number",
                                "description": "Depth limit, default 3",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": FilesTool.read_file_contents.__name__,
                    "description": FilesTool.read_file_contents.__doc__,
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
            {
                "type": "function",
                "function": {
                    "name": FilesTool.read_directory_contents.__name__,
                    "description": FilesTool.read_directory_contents.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of directory relative to current dir",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
        ]