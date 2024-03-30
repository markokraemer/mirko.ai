import subprocess
from .base import Tool, ToolResult
from ..utils.workspace_utils import get_docker_container_id
from ..memory.working_memory import WorkingMemory
import os
import tempfile
import time
import re

class TerminalTool(Tool):
    def __init__(self):
        self.logs_dir = tempfile.mkdtemp()
        container_id = get_docker_container_id("workspace_dev-env_1")
        if container_id is None:
            raise ValueError("No running container found for the standard docker image.")
        self.container_name = container_id
        self.working_memory = WorkingMemory()
        self.initialize_terminal_sessions()

    def initialize_terminal_sessions(self):
        # Initialize the Terminal_Sessions module with an empty list
        self.working_memory.add_or_update_module("Terminal_Sessions", [])

    def new_terminal_session(self) -> str:
        terminal_sessions = self.working_memory.get_module("Terminal_Sessions")
        session_id = f"session_{len(terminal_sessions) + 1}"
        log_file_path = os.path.join(self.logs_dir, f"{session_id}.log")
        # Ensure to kill a previous version of the tmux session if it exists
        kill_command = f"tmux kill-session -t {session_id}"
        subprocess.run(kill_command, shell=True)  # Ignore errors if session does not exist
        # Create a new tmux session for the docker exec command with logging
        try:
            # Using script to capture session output, including timestamps
            command = f"tmux new-session -d -s {session_id} 'script -q -f {log_file_path} -c \"docker exec -it {self.container_name} /bin/bash\"'"
            subprocess.run(command, shell=True, check=True)
            terminal_sessions.append({"session_id": session_id, "session_history": []})
            self.working_memory.add_or_update_module("Terminal_Sessions", terminal_sessions)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create new tmux session for {session_id}")
        return session_id

    def close_terminal_session(self, session_id: str):
        # Kill the tmux session
        try:
            command = f"tmux kill-session -t {session_id}"
            subprocess.run(command, shell=True, check=True)
            # Update the session module from working memory to remove the closed session
            terminal_sessions = self.working_memory.get_module("Terminal_Sessions")
            terminal_sessions = [session for session in terminal_sessions if session["session_id"] != session_id]
            self.working_memory.add_or_update_module("Terminal_Sessions", terminal_sessions)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to kill tmux session {session_id}")

    def send_terminal_command(self, session_id: str, command: str) -> ToolResult:
        # Send command to the tmux session
        tmux_command = f"tmux send-keys -t {session_id} '{command}' Enter"
        try:
            subprocess.run(tmux_command, shell=True, check=True)
            # Update the session history from the log file after sending the command
            time.sleep(5)
            self.get_and_update_terminal_session_history(session_id)
            return ToolResult(success=True, output="Command executed", exit_code=0)
        except subprocess.CalledProcessError as e:
            return ToolResult(success=False, output="Failed to send command to tmux session", exit_code=1)

    def get_and_update_terminal_session_history(self, session_id: str) -> str:
        """Returns the command history of a terminal session, including timestamps."""
        terminal_sessions = self.working_memory.get_module("Terminal_Sessions")
        for session in terminal_sessions:
            if session["session_id"] == session_id:
                log_file_path = os.path.join(self.logs_dir, f"{session_id}.log")
                try:
                    with open(log_file_path, 'r') as log_file:
                        log_content = log_file.read()
                        # General formatting solution: Remove ANSI escape sequences and other non-text content
                        clean_log_content = re.sub(r'\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]|\x1b\]=.*?\x07', '', log_content)
                        # Further clean-up to remove specific non-text content if needed
                        clean_log_content = re.sub(r'Script started.*?\n|Script done.*?\n', '', clean_log_content)
                        new_session_history = clean_log_content.splitlines()
                        session["session_history"] = new_session_history  # Entirely replace the session_history
                        self.working_memory.add_or_update_module("Terminal_Sessions", terminal_sessions)
                        return "\n".join(new_session_history)
                except FileNotFoundError:
                    return "Log file not found. It's possible the session has not generated any output yet."
        return "Session not found or no history available."
    
    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the JSON schema for TerminalTool function calls.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": TerminalTool.new_terminal_session.__name__,
                    "description": TerminalTool.new_terminal_session.__doc__,
                    "parameters": {},
                    "returns": {
                        "type": "string",
                        "description": "The session ID of the newly created terminal session.",
                    }
                },
            },
            {
                "type": "function",
                "function": {
                    "name": TerminalTool.close_terminal_session.__name__,
                    "description": TerminalTool.close_terminal_session.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "The session ID of the terminal session to close.",
                            }
                        },
                        "required": ["session_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": TerminalTool.send_terminal_command.__name__,
                    "description": TerminalTool.send_terminal_command.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "The session ID of the terminal session to send the command to.",
                            },
                            "command": {
                                "type": "string",
                                "description": "The command to send to the terminal session.",
                            }
                        },
                        "required": ["session_id", "command"],
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "success": {
                                "type": "boolean",
                                "description": "Indicates if the command was successfully sent and executed.",
                            },
                            "output": {
                                "type": "string",
                                "description": "The output message from the execution of the command.",
                            },
                            "exit_code": {
                                "type": "number",
                                "description": "The exit code of the command execution.",
                            }
                        },
                        "required": ["success", "output", "exit_code"],
                    }
                },
            },
        ]

if __name__ == "__main__":
    # Initialize the TerminalTool instance
    terminal_tool_instance = TerminalTool()

    # Generate the first terminal session
    first_session_id = terminal_tool_instance.new_terminal_session()
    print(f"Generated first terminal session ID: {first_session_id}")

    # Dispatch a command to the first terminal session
    first_command = "cd frontend && npm install"
    first_execution_result = terminal_tool_instance.send_terminal_command(first_session_id, first_command)
    print(f"Dispatched command to first session: {first_command}\nExecution Result: {first_execution_result.output}")

    # Generate the second terminal session
    second_session_id = terminal_tool_instance.new_terminal_session()
    print(f"Generated second terminal session ID: {second_session_id}")

    # Dispatch a command to the second terminal session
    second_command = "cd backend && npm install"
    second_execution_result = terminal_tool_instance.send_terminal_command(second_session_id, second_command)
    print(f"Dispatched command to second session: {second_command}\nExecution Result: {second_execution_result.output}")

    # Terminate the first terminal session
    terminal_tool_instance.close_terminal_session(first_session_id)
    print(f"First terminal session with ID {first_session_id} has been terminated.")

    # # Terminate the second terminal session
    # terminal_tool_instance.close_terminal_session(second_session_id)
    # print(f"Second terminal session with ID {second_session_id} has been terminated.")
