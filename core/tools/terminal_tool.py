import docker
from .base import Tool, ToolResult
from ..utils.workspace_utils import get_docker_container_id
from ..memory.working_memory_db import WorkingMemoryDB
import json
import uuid

class TerminalTool(Tool):
    def __init__(self):
        self.client = docker.from_env()
        self.db = WorkingMemoryDB()  # Using default db path as per instructions
        self._initialize_db()
        container_id = get_docker_container_id("workspace_dev-env_1")  # Hard coded Docker Image Name
        if container_id is None:
            raise ValueError("No running container found for the standard docker image.")
        self.container = self.client.containers.get(container_id)

    def _initialize_db(self):
        # Initialize the database with an empty dictionary for terminal sessions if it doesn't exist
        sessions = self.db.get_entries("Terminal_Sessions")
        if not sessions:
            self.db.add_entry("Terminal_Sessions", json.dumps({}))

    def new_terminal_session(self) -> str:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        session_data = {
            "container_id": self.container.id,
            "logs": [],
            "active": True
        }
        self._update_session_data(session_id, session_data)
        return session_id

    def close_terminal_session(self, session_id: str):
        self.db.remove_entry(session_id)  # Remove the session entry completely as per updated instructions

    def send_terminal_command(self, session_id: str, command: str) -> ToolResult:
        session_data = self._get_session_data(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found.")
        result = self.container.exec_run(command, tty=True)
        session_data["logs"].append({"command": command, "output": result.output.decode('utf-8'), "exit_code": result.exit_code})
        session_data["active"] = False  # Mark the session as not busy after executing the command
        self._update_session_data(session_id, session_data)
        return ToolResult(
            success=(result.exit_code == 0),
            output=result.output.decode('utf-8'),
            exit_code=result.exit_code,
        )

    def get_session_log(self, session_id: str):
        session_data = self._get_session_data(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found.")
        return session_data["logs"]

    def _get_session_data(self, session_id: str):
        sessions = json.loads(self.db.get_entries("Terminal_Sessions")[0]['data'])
        return sessions.get(session_id)

    def _update_session_data(self, session_id: str, session_data: dict):
        sessions = json.loads(self.db.get_entries("Terminal_Sessions")[0]['data'])
        sessions[session_id] = session_data
        self.db.update_entry("Terminal_Sessions", json.dumps(sessions))

