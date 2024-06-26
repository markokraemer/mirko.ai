import os
import logging
from .base import Tool, ToolResult
from ..utils.llm import make_llm_api_call
from ..utils.file_utils import find_files, EXCLUDED_FILES, EXCLUDED_DIRS, EXCLUDED_EXT, _should_exclude
import json
from ..memory.working_memory import WorkingMemory



def _rindex(li, value):
    return len(li) - li[-1::-1].index(value) - 1

class FilesTool(Tool):
    def __init__(self):
        """
        Initialize the FilesTool with a base path and a working memory instance.
        """
        logging.info("Initializing FilesTool")
        self.base_path = "/root/softgen.ai/mirko.ai/working_directory" # Hard coded for now
        self.working_memory = WorkingMemory()        
        self.initialize_files()
        logging.info("FilesTool initialized successfully")

    def initialize_files(self):
        """
        Initialize the files in the working directory by reading the directory contents.
        """
        logging.info("Initializing files in the working directory")
        if not self.working_memory.get_module("WorkspaceDirectoryContents"):
            self.working_memory.add_or_update_module("WorkspaceDirectoryContents", [])
        self.read_directory_contents("") # Hardcoded initialises with full latest WorkspaceDirectoryContents
        logging.info("Files in the working directory initialized successfully")

    def _get_effective_path(self, path: str) -> str:
        """
        Get the effective path by handling . and ~ to avoid touching things outside base_path.
        
        :param path: The path to process.
        :return: The effective path.
        """
        logging.info(f"Getting effective path for: {path}")
        # Handling . and ~ to avoid touching things outside base_path.
        path_parts = path.split(os.sep)
        if "." in path_parts:
            remaining_path = path_parts[_rindex(path_parts, ".") + 1 :]
            effective_path = os.path.join(self.base_path, *remaining_path)
        else:
            effective_path = os.path.join(self.base_path, path)
        logging.info(f"Effective path obtained: {effective_path}")
        return effective_path


# <----> Specialised Actions

    def edit_file_contents(self, file_path: str, instructions: str) -> ToolResult:
        """
        Edit file contents based on instructions.
        
        :param file_path: Path to the file to be edited.
        :param instructions: Instructions on how to edit the file.
        :return: Result of the editing operation.
        """
        logging.info(f"Editing file contents for: {file_path} with instructions: {instructions}")
        effective_path = self._get_effective_path(file_path)
        if not os.path.exists(effective_path):
            logging.error(f"File {file_path} does not exist.")
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
            # Make LLM API call and parse the response
            logging.info(f"Making LLM API call for editing file: {file_path}")
            response = make_llm_api_call(messages, "gpt-4-turbo-preview", json_mode=True, max_tokens=4096) 
            response_content = response.choices[0].message['content']
            logging.info(f"LLM API call response received for file edit: {file_path}")
            response_json = json.loads(response_content)
            new_content = response_json["File"]["newFileContents"]

            # Write the new content into the file
            with open(effective_path, 'w') as file:
                file.write(new_content)
            
            # Read the updated file content to include in the success response
            with open(effective_path, 'r') as file:
                updated_content = file.read()
                
            logging.info(f"File {file_path} edited successfully. Latest content updated.")
            return self.success_response(f"File {file_path} edited successfully. Latest content: {updated_content}")
        except Exception as e:
            logging.error(f"An error occurred while editing file contents for {file_path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)

# <----> Basic File Ops

    def create_file(self, file_path: str) -> ToolResult:
        """
        Create a file at file_path, path is relative to current dir. Create the directory too if it's given in the path.
        """
        logging.info(f"Creating file at path: {file_path}")
        effective_path = self._get_effective_path(file_path)
        if os.path.exists(effective_path):
            logging.error("File already exists")
            return self.fail_response("File already exists")
        try:
            os.makedirs(os.path.dirname(effective_path), exist_ok=True)
            with open(effective_path, 'w') as file:
                file.close()
            logging.info(f"File {file_path} created successfully")
            return self.success_response(f"File {file_path} created successfully")
        except Exception as e:
            logging.error(f"An error occurred while creating file at {file_path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)

    def move_file(self, current_file_path: str, new_file_path: str) -> ToolResult:
        """
        Move a file from current_file_path to new_file_path, both paths are relative to current dir
        """
        logging.info(f"Moving file from {current_file_path} to {new_file_path}")
        current_effective_path = self._get_effective_path(current_file_path)
        new_effective_path = self._get_effective_path(new_file_path)
        if not os.path.exists(current_effective_path):
            logging.error("Current file does not exist")
            return self.fail_response("Current file does not exist")
        try:
            os.rename(current_effective_path, new_effective_path)
            logging.info(f"File moved from {current_file_path} to {new_file_path}")
            return self.success_response(f"File renamed from {current_file_path} to {new_file_path}")
        except Exception as e:
            logging.error(f"An error occurred while moving file from {current_file_path} to {new_file_path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)

    def rename_file(self, old_file_path: str, new_file_path: str) -> ToolResult:
        """
        Rename a file from old_file_path to new_file_path, paths are relative to current dir
        """
        logging.info(f"Renaming file from {old_file_path} to {new_file_path}")
        old_effective_path = self._get_effective_path(old_file_path)
        new_effective_path = self._get_effective_path(new_file_path)
        if not os.path.exists(old_effective_path):
            logging.error("Old file does not exist")
            return self.fail_response("Old file does not exist")
        if os.path.exists(new_effective_path):
            logging.error("New file name already exists")
            return self.fail_response("New file name already exists")
        try:
            os.rename(old_effective_path, new_effective_path)
            logging.info(f"File renamed from {old_file_path} to {new_file_path}")
            return self.success_response(f"File renamed from {old_file_path} to {new_file_path}")
        except Exception as e:
            logging.error(f"An error occurred while renaming file from {old_file_path} to {new_file_path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)

    def delete_file(self, file_path: str) -> ToolResult:
        """
        Delete the file at file_path, path is relative to current dir
        """
        logging.info(f"Deleting file at path: {file_path}")
        effective_path = self._get_effective_path(file_path)
        if not os.path.exists(effective_path):
            logging.error("File does not exist")
            return self.fail_response("File does not exist")
        try:
            os.remove(effective_path)
            logging.info(f"File {file_path} deleted successfully")
            return self.success_response(f"File {file_path} deleted successfully")
        except Exception as e:
            logging.error(f"An error occurred while deleting file at {file_path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)


# <----> Retrieval

    def get_file_tree(self, path: str, depth: int = 3) -> ToolResult:
        """
        List path recursively with limited depth. Path is relative to current dir.
        """
        logging.info(f"Getting file tree for path: {path} with depth: {depth}")
        if not os.path.exists(self.base_path):
            logging.error("Base path does not exist")
            return self.fail_response("Base path does not exist")

        if "~" in path:
            logging.error("Path cannot contain ~")
            return self.fail_response("Path cannot contain ~")
        effective_path = self._get_effective_path(path)
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            logging.error("Path is not within the base path")
            return ToolResult(
                success=False, output="Path is not within the base path", exit_code=1
            )
        try:
            listed_paths = find_files(effective_path, depth)
            logging.info(f"File tree retrieved successfully for path: {path}")
            return self.success_response({"paths": listed_paths})
        except Exception as e:
            logging.error(f"An error occurred while getting file tree for path: {path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)

    def read_file_contents(self, path: str) -> ToolResult:
        """
        Show the contents of the file at path relative to current dir
        """
        logging.info(f"Reading file contents for path: {path}")
        if not os.path.exists(self.base_path):
            logging.error("Base path does not exist")
            return self.fail_response("Base path does not exist")
        effective_path = self._get_effective_path(path)
        if not os.path.commonpath([self.base_path, effective_path]) == os.path.normpath(
            self.base_path
        ):
            logging.error("Path is not within the base path")
            return ToolResult(
                success=False, output="Path is not within the base path", exit_code=1
            )
        if os.path.exists(effective_path):
            with open(effective_path, "r") as file:
                text = file.read()
            logging.info(f"File contents read successfully for path: {path}")
            return self.success_response(text)
        else:
            logging.error("File does not exist")
            return self.fail_response("File does not exist")

    def read_directory_contents(self, path: str, depth: int = 3) -> ToolResult:
        """
        List all files and directories at the given path, including their contents, while excluding certain files and directories as specified in file_utils.py, up to a specified depth. Updates the WorkspaceDirectoryContents Module in working memory with the directory contents.
        """
        logging.info(f"Reading directory contents for path: {path} with depth: {depth}")
        if not os.path.exists(self.base_path):
            logging.error("Base path does not exist")
            return self.fail_response("Base path does not exist")
        effective_path = self._get_effective_path(path)
        if not os.path.exists(effective_path) or not os.path.isdir(effective_path):
            logging.error("Directory does not exist or is not a directory")
            return self.fail_response("Directory does not exist or is not a directory")

        try:
            directory_contents = {}
            for root, dirs, files in os.walk(effective_path):
                # Calculate current depth
                current_depth = os.path.relpath(root, effective_path).count(os.sep)
                if current_depth > depth:
                    dirs[:] = []  # Don't go any deeper
                else:
                    # Apply exclusions for directories
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not _should_exclude(self.base_path, os.path.join(root, d))]
                    # Apply exclusions for files
                    files = [f for f in files if f not in EXCLUDED_FILES and not any(f.endswith(ext) for ext in EXCLUDED_EXT) and not _should_exclude(self.base_path, os.path.join(root, f))]
                    # Append relative paths of files and directories to contents and read file contents
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_file_path = os.path.relpath(file_path, effective_path)
                        if not _should_exclude(self.base_path, file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as file_content:
                                    directory_contents[relative_file_path] = file_content.read()
                            except UnicodeDecodeError:
                                # Skip files that cannot be decoded with UTF-8
                                continue
            # Update the WorkspaceDirectoryContents Module in working memory
            self.working_memory.add_or_update_module("WorkspaceDirectoryContents", directory_contents)
            logging.info(f"Directory contents read successfully for path: {path}")
            return self.success_response({"contents": directory_contents})
        except Exception as e:
            logging.error(f"An error occurred while reading directory contents for path: {path}: {e}", exc_info=True)
            return ToolResult(success=False, output=str(e), exit_code=1)


    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the OpenAPI JSON schema for function calls.
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
            # {
            #     "type": "function",
            #     "function": {
            #         "name": FilesTool.rename_file.__name__,
            #         "description": FilesTool.rename_file.__doc__,
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "old_file_path": {
            #                     "type": "string",
            #                     "description": "Old path of the file, relative to current dir",
            #                 },
            #                 "new_file_path": {
            #                     "type": "string",
            #                     "description": "New path for the file, relative to current dir",
            #                 }
            #             },
            #             "required": ["old_file_path", "new_file_path"],
            #         },
            #     },
            # },
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


if __name__ == "__main__":
    logging.info("FilesTool script execution started")
    # Initialize the FilesTool instance
    files_tool_instance = FilesTool()

    # # Step 1: Example usage of creating a new file
    # new_file_path = "examples/new_sample.txt"
    # create_file_result = files_tool_instance.create_file(new_file_path)
    # print(f"Creating new file '{new_file_path}': {create_file_result.output}")
    # input("Press ENTER to continue...")

    # # Step 2: Example usage of moving the created file
    # moved_file_path = "examples/moved_sample.txt"
    # move_file_result = files_tool_instance.move_file(new_file_path, moved_file_path)
    # print(f"Moving file from '{new_file_path}' to '{moved_file_path}': {move_file_result.output}")
    # input("Press ENTER to continue...")

    # # Step 3: Example usage of editing file contents
    # edit_instructions = "Add a function to return the sum of two numbers."
    # edit_file_result = files_tool_instance.edit_file_contents(moved_file_path, edit_instructions)
    # print(f"Editing file '{moved_file_path}' with instructions '{edit_instructions}': {edit_file_result.output}")
    # input("Press ENTER to continue...")

    # # Step 4: Example usage of renaming the edited file
    # renamed_file_path = "examples/renamed_sample.txt"
    # rename_file_result = files_tool_instance.rename_file(moved_file_path, renamed_file_path)
    # print(f"Renaming file from '{moved_file_path}' to '{renamed_file_path}': {rename_file_result.output}")
    # input("Press ENTER to continue...")

    # # Step 5: Example usage of getting the file tree
    # file_tree_path = "examples"
    # file_tree_result = files_tool_instance.get_file_tree(file_tree_path)
    # print(f"File tree of '{file_tree_path}': {file_tree_result.output}")
    # input("Press ENTER to continue...")

    # # Step 6: Example usage of reading file contents
    # read_file_result = files_tool_instance.read_file_contents(renamed_file_path)
    # print(f"Contents of file '{renamed_file_path}': {read_file_result.output}")
    # input("Press ENTER to continue...")

    # Step 7: Example usage of reading directory contents
    list_directory_path = ""
    list_directory_result = files_tool_instance.read_directory_contents(list_directory_path)
    print(f"Contents of directory '{list_directory_path}': {list_directory_result.output}")
    input("Press ENTER to continue...")
    # # Step 8: Example usage of deleting the renamed file
    # delete_file_result = files_tool_instance.delete_file(renamed_file_path)
    # print(f"Deleting file '{renamed_file_path}': {delete_file_result.output}")
    # input("Press ENTER to continue..."
    logging.info("FilesTool script execution completed")

