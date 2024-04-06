from core.memory.working_memory import WorkingMemory
from .base import Tool, ToolResult
import json
import time

class TaskTool(Tool):
    def __init__(self):
        """Initialize the TaskTool with a working memory instance and an empty task list."""
        self.working_memory = WorkingMemory()
        self.initialize_task_list()

    def initialize_task_list(self):
        """Check if the TaskList module exists in working memory; if not, initialize it with an empty list."""
        if not self.working_memory.get_module("TaskList"):
            self.working_memory.add_or_update_module("TaskList", [])

    def add_task(self, task_id: str, instructions: str, resources: list) -> ToolResult:
        """
        Add a new task to the task list in working memory.
        
        Parameters:
        - task_id (str): The unique identifier for the task.
        - instructions (str): Detailed instructions for the task.
        - resources (list): A list of resources needed for the task.
        
        Returns:
        - ToolResult: The result of the operation, indicating success or failure.
        """
        task_list = self.working_memory.get_module("TaskList")
        task = {
            "Task": {
                "ID": task_id,
                "Instructions": instructions,
                "Resources": resources
            }
        }
        task_list.append(task)
        self.working_memory.add_or_update_module("TaskList", task_list)
        return ToolResult(success=True, output="Task added successfully.", exit_code=0)

    def remove_task(self, task_id: str) -> ToolResult:
        """
        Remove a task from the task list in working memory based on its ID.
        
        Parameters:
        - task_id (str): The unique identifier for the task to be removed.
        
        Returns:
        - ToolResult: The result of the operation, indicating success or failure.
        """
        task_list = self.working_memory.get_module("TaskList")
        removed_task = [task for task in task_list if task["Task"]["ID"] == task_id]
        task_list = [task for task in task_list if task["Task"]["ID"] != task_id]
        self.working_memory.add_or_update_module("TaskList", task_list)
        if removed_task:
            removed_task_json = json.dumps(removed_task[0], indent=4)
            return ToolResult(success=True, output=f"Task removed successfully: {removed_task_json}", exit_code=0)
        else:
            return ToolResult(success=False, output="Task ID not found.", exit_code=1)


    def update_task(self, task_id: str, instructions: str = None, resources: list = None) -> ToolResult:
        """
        Update the details of an existing task in the task list in working memory.
        
        Parameters:
        - task_id (str): The unique identifier for the task to be updated.
        - instructions (str, optional): Updated instructions for the task.
        - resources (list, optional): Updated list of resources for the task.
        
        Returns:
        - ToolResult: The result of the operation, indicating success or failure.
        """
        task_list = self.working_memory.get_module("TaskList")
        for task in task_list:
            if task["Task"]["ID"] == task_id:
                if instructions:
                    task["Task"]["Instructions"] = instructions
                if resources:
                    task["Task"]["Resources"] = resources
                break
        self.working_memory.add_or_update_module("TaskList", task_list)
        return ToolResult(success=True, output="Task updated successfully.", exit_code=0)

    
    # async def select_and_execute_task(self, task_id: str) -> ToolResult:
    #     """
    #     Select a task by its ID and simulate its execution.
        
    #     Parameters:
    #     - task_id (str): The unique identifier for the task to be selected and executed.
        
    #     Returns:
    #     - ToolResult: The result of the operation, indicating success or failure.
    #     """
    #     task_list = self.working_memory.get_module("TaskList")
    #     selected_task = next((task for task in task_list if task["Task"]["ID"] == task_id), None)

    #     if selected_task:

    #         user_request = {json.dumps(selected_task, indent=4)}

    #         from core.run_session import start_session_run_implementation
            
    #         task_summary = await start_session_run_implementation(user_request)

    #         return ToolResult(success=True, output=f"Task was completed with following summary: {task_summary}", exit_code=0)
    #     else:
    #         return ToolResult(success=False, output="Task ID not found.", exit_code=1)

    async def select_and_execute_task(self, task_id: str) -> ToolResult:
        """
        Select a task by its ID and simulate its execution.
        
        Parameters:
        - task_id (str): The unique identifier for the task to be selected and executed.
        
        Returns:
        - ToolResult: The result of the operation, indicating success or failure.
        """
        task_list = self.working_memory.get_module("TaskList")
        selected_task = next((task for task in task_list if task["Task"]["ID"] == task_id), None)

        if selected_task:
            # Add a message indicating the current focus before the selected task in the new memory module
            current_focus_message = "I AM CURRENTLY WORKING ON COMPLETING THIS TASK: "
            self.working_memory.add_or_update_module("CurrentFocus", [current_focus_message + json.dumps(selected_task)])

            return ToolResult(success=True, output=f"Updated the WorkingMemory 'CurrentFocus' – Now start working on the selected Task!", exit_code=0)
        else:
            return ToolResult(success=False, output="Task ID not found.", exit_code=1)
    
    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the OpenAPI JSON schema for function calls in the Task Planning Tool.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": TaskTool.add_task.__name__,
                    "description": TaskTool.add_task.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The unique identifier for the task.",
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Detailed instructions for the task.",
                            },
                            "resources": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "A list of resources needed for the task.",
                            }
                        },
                        "required": ["task_id", "instructions", "resources"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": TaskTool.remove_task.__name__,
                    "description": TaskTool.remove_task.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The unique identifier for the task to be removed.",
                            }
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": TaskTool.update_task.__name__,
                    "description": TaskTool.update_task.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The unique identifier for the task to be updated.",
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Updated instructions for the task.",
                            },
                            "resources": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Updated list of resources for the task.",
                            }
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": TaskTool.select_and_execute_task.__name__,
                    "description": TaskTool.select_and_execute_task.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The unique identifier for the task to be selected and executed.",
                            }
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

if __name__ == "__main__":
    # Initialize the TaskTool instance
    task_tool_instance = TaskTool()

    # Sample usage of adding a task
    add_task_result = task_tool_instance.add_task("task_001", "Fix the bug in the login feature", ["codebase access"])
    print(f"Add Task Result: {add_task_result.output}")

    # Sample usage of removing a task
    remove_task_result = task_tool_instance.remove_task("task_001")
    print(f"Remove Task Result: {remove_task_result.output}")

    # Sample usage of updating a task
    update_task_result = task_tool_instance.update_task("task_002", instructions="Update the database schema", resources=["database access"])
    print(f"Update Task Result: {update_task_result.output}")

    # Sample usage of selecting and executing a task
    select_and_execute_task_result = task_tool_instance.select_and_execute_task("task_001")
    print(f"Select and Execute Task Result: {select_and_execute_task_result.output}")