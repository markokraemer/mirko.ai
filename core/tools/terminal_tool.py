import subprocess
from .base import Tool, ToolResult
from ..utils.workspace_utils import get_docker_container_id
from ..memory.working_memory import WorkingMemory
import os
import tempfile
import time
import re
import logging

class TerminalTool(Tool):
    def __init__(self):
        """
        Initializes the TerminalTool instance by setting up a temporary directory for logs,
        retrieving the container ID, and initializing terminal sessions.
        """
        logging.info("Initializing TerminalTool instance")
        self.logs_dir = tempfile.mkdtemp()
        container_id = get_docker_container_id("workspace_dev-env_1")
        if container_id is None:
            logging.error("No running container found for the standard docker image.")
            raise ValueError("No running container found for the standard docker image.")
        self.container_name = container_id
        self.working_memory = WorkingMemory()
        self.initialize_terminal_sessions()
        logging.info("TerminalTool instance initialized successfully")

    def initialize_terminal_sessions(self):
        """
        Initializes the TerminalSessions module with an empty list if it doesn't already exist.
        """
        logging.info("Initializing terminal sessions")
        if not self.working_memory.get_module("TerminalSessions"):
            self.working_memory.add_or_update_module("TerminalSessions", [])
        logging.info("Terminal sessions initialized successfully")

    def new_terminal_session(self) -> str:
        """
        Creates a new terminal session and returns its session ID.
        """
        logging.info("Creating new terminal session")
        terminal_sessions = self.working_memory.get_module("TerminalSessions")
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
            terminal_sessions.append({"session_id": session_id, "action_history": [], "session_history": []})
            self.working_memory.add_or_update_module("TerminalSessions", terminal_sessions)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create new tmux session for {session_id}: {e}")
            raise RuntimeError(f"Failed to create new tmux session for {session_id}")
        logging.info(f"New terminal session created with ID: {session_id}")
        return session_id

    def close_terminal_session(self, session_id: str) -> ToolResult:
        """
        Closes the specified terminal session and returns a ToolResult indicating success or failure.
        """
        logging.info(f"Closing terminal session with ID: {session_id}")
        # Kill the tmux session
        try:
            command = f"tmux kill-session -t {session_id}"
            subprocess.run(command, shell=True, check=True)
            # Update the session module from working memory to remove the closed session
            terminal_sessions = self.working_memory.get_module("TerminalSessions")
            closed_session = [session for session in terminal_sessions if session["session_id"] == session_id]
            terminal_sessions = [session for session in terminal_sessions if session["session_id"] != session_id]
            self.working_memory.add_or_update_module("TerminalSessions", terminal_sessions)
            if closed_session:
                logging.info(f"Closed terminal session with ID: {session_id}")
                return ToolResult(success=True, output=f"CLOSED session_id: {closed_session[0]}", exit_code=0)
            else:
                logging.info(f"Session ID not found for closing: {session_id}")
                return ToolResult(success=False, output="Session ID not found", exit_code=1)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to close terminal session {session_id}: {e}")
            return ToolResult(success=False, output=f"Failed to kill tmux session {session_id}", exit_code=1)
    
    def send_terminal_command(self, session_id: str, command: str) -> ToolResult:
        """
        Sends a command to the specified terminal session and updates the session's action and history.
        """
        logging.info(f"Sending command to terminal session {session_id}: {command}")
        tmux_command = f"tmux send-keys -t {session_id} '{command}' Enter"
        try:
            subprocess.run(tmux_command, shell=True, check=True)
            time.sleep(5)  # Wait for the command to be executed and logged
            self.update_action_history(session_id, command)
            self.get_latest_terminal_session_history(session_id)
            logging.info(f"Command sent successfully to terminal session {session_id}: {command}")
            return ToolResult(success=True, output="Command executed", exit_code=0)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to send command to tmux session {session_id}: {e}")
            return ToolResult(success=False, output="Failed to send command to tmux session", exit_code=1)

    def update_action_history(self, session_id: str, command: str):
        """Updates the action history of a terminal session with the command sent."""
        logging.info(f"Updating action history for terminal session {session_id} with command: {command}")
        terminal_sessions = self.working_memory.get_module("TerminalSessions")
        for session in terminal_sessions:
            if session["session_id"] == session_id:
                session["action_history"].append(command)
                self.working_memory.add_or_update_module("TerminalSessions", terminal_sessions)
                logging.info(f"Action history updated for terminal session {session_id} with command: {command}")
                break

    def get_latest_terminal_session_history(self, session_id: str) -> str:
        """Returns the command history of a terminal session, including timestamps."""
        logging.info(f"Retrieving latest terminal session history for session ID: {session_id}")
        terminal_sessions = self.working_memory.get_module("TerminalSessions")
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
                        self.working_memory.add_or_update_module("TerminalSessions", terminal_sessions)
                        logging.info(f"Latest terminal session history retrieved for session ID: {session_id}")
                        return "\n".join(new_session_history)
                except FileNotFoundError:
                    logging.error(f"Log file not found for session ID: {session_id}. It's possible the session has not generated any output yet.")
                    return "Log file not found. It's possible the session has not generated any output yet."
        logging.info(f"Session not found or no history available for session ID: {session_id}")
        return "Session not found or no history available."
    
    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the OpenAPI JSON schema for function calls.
        """
        return [
            # {
            #     "type": "function",
            #     "function": {
            #         "name": TerminalTool.new_terminal_session.__name__,
            #         "description": TerminalTool.new_terminal_session.__doc__,
            #         "parameters": {},
            #     },
            # },
            # {
            #     "type": "function",
            #     "function": {
            #         "name": TerminalTool.close_terminal_session.__name__,
            #         "description": TerminalTool.close_terminal_session.__doc__,
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "session_id": {
            #                     "type": "string",
            #                     "description": "The session ID of the terminal session to close.",
            #                 }
            #             },
            #             "required": ["session_id"],
            #         },
            #     },
            # },
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
                                "description": "The session ID to which the command will be sent.",
                            },
                            "command": {
                                "type": "string",
                                "description": "The command to be executed in the terminal session.",
                            }
                        },
                        "required": ["session_id", "command"],
                    },
                },
            },
        {
            "type": "function",
            "function": {
                "name": TerminalTool.get_latest_terminal_session_history.__name__,
                "description": TerminalTool.get_latest_terminal_session_history.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "The session ID for which the command history will be retrieved.",
                        }
                    },
                    "required": ["session_id"],
                },
            },
        },
        ]

if __name__ == "__main__":
    # Initialize the TerminalTool instance
    logging.info("Initializing TerminalTool for main execution")
    terminal_tool_instance = TerminalTool()

    # Generate the first terminal session
    first_session_id = terminal_tool_instance.new_terminal_session()
    logging.info(f"Generated first terminal session ID: {first_session_id}")

    # Dispatch a command to the first terminal session
    first_command = "cd frontend && npm install"
    logging.info(f"Dispatching command to first session: {first_command}")
    first_execution_result = terminal_tool_instance.send_terminal_command(first_session_id, first_command)
    logging.info(f"Dispatched command to first session: {first_command}\nExecution Result: {first_execution_result.output}")

    # Generate the second terminal session
    second_session_id = terminal_tool_instance.new_terminal_session()
    logging.info(f"Generated second terminal session ID: {second_session_id}")

    # Dispatch a command to the second terminal session
    second_command = "cd backend && npm install"
    logging.info(f"Dispatching command to second session: {second_command}")
    second_execution_result = terminal_tool_instance.send_terminal_command(second_session_id, second_command)
    print(f"Dispatched command to second session: {second_command}\nExecution Result: {second_execution_result.output}")

    # # Terminate the first terminal session
    # terminal_tool_instance.close_terminal_session(first_session_id)
    # logging.info(f"Dispatched command to second session: {second_command}\nExecution Result: {second_execution_result.output}")


    # # Terminate the second terminal session
    # logging.info(f"Terminating first terminal session with ID {first_session_id}")
    # terminal_tool_instance.close_terminal_session(second_session_id)
    # logging.info(f"First terminal session with ID {first_session_id} has been terminated.")

