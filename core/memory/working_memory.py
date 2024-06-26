import sqlite3
import json
import logging

class WorkingMemory:
    def __init__(self, db_path="db.db"):
        logging.info("Initializing WorkingMemory with db_path: {}".format(db_path))
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        logging.info("Creating tables in WorkingMemory")
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MemoryModules (
                id INTEGER PRIMARY KEY,
                module_name TEXT UNIQUE,
                data TEXT
            )
        ''')
        self.conn.commit()
        logging.info("Tables created successfully in WorkingMemory")

    def add_or_update_module(self, module_name, data):
        logging.info("Adding or updating module: {}".format(module_name))
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO MemoryModules (module_name, data) VALUES (?, ?)
            ON CONFLICT(module_name) DO UPDATE SET data = excluded.data
        ''', (module_name, json.dumps(data)))
        self.conn.commit()
        logging.info("Module added or updated successfully: {}".format(module_name))

    def get_module(self, module_name):
        logging.info("Retrieving module: {}".format(module_name))
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM MemoryModules WHERE module_name = ?', (module_name,))
        module_data = cursor.fetchone()
        logging.info("Module retrieved successfully: {}".format(module_name))
        return json.loads(module_data[0]) if module_data else None

    def delete_module(self, module_name):
        logging.info("Deleting module: {}".format(module_name))
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM MemoryModules WHERE module_name = ?', (module_name,))
        self.conn.commit()
        logging.info("Module deleted successfully: {}".format(module_name))

    def export_memory(self):
        logging.info("Exporting memory from WorkingMemory")
        cursor = self.conn.cursor()
        cursor.execute('SELECT module_name, data FROM MemoryModules')
        modules = cursor.fetchall()
        memory_structure = {}
        for module_name, data in modules:
            memory_structure[module_name] = json.loads(data)
        logging.info("Memory exported successfully from WorkingMemory")
        return memory_structure

    def clear_memory(self):
        logging.info("Clearing memory in WorkingMemory")
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM MemoryModules')
        self.conn.commit()
        logging.info("Memory cleared successfully in WorkingMemory")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Create an instance of the WorkingMemory
    working_memory = WorkingMemory('db.db')

    # Example usage
    working_memory.add_or_update_module("Objective", "Build a simple Landing Page for my construction company.")
    working_memory.add_or_update_module("TerminalSessions", [
        {
            "session_id": "1",
            "active": True,
            "terminal_log": [
                "2023-03-15T09:00:00 New_terminal_session: Session 1 started",
                "2023-03-15T09:01:00 Command: echo 'Hello World!', Output: Hello World!",
                "2023-03-15T09:10:00 Close_terminal_session: Session 1 closed"
            ]
        },
        {
            "session_id": "2",
            "active": False,
            "terminal_log": [
                "2023-03-15T10:00:00 New_terminal_session: Session 2 started",
                "2023-03-15T10:01:00 Command: pwd, Output: /home/user",
                "2023-03-15T10:02:00 Command: ls -la, Output : total 28\ndrwxr-xr-x 7 user user 4096 Mar 15 10:02 .\ndrwxr-xr-x 3 root root 4096 Mar 14 09:53 ..",
                "2023-03-15T10:10:00 Close_terminal_session: Session 2 closed"
            ]
        }
    ])
    working_memory.add_or_update_module("TaskList", [
        {"task_id": "1", "instruction": "First Instruction"},
        {"task_id": "2", "instruction": "Second Instruction"},
        {"task_id": "3", "instruction": "Third Instruction"}
    ])

    # Updating a module example
    updated_task_list = [
        {"task_id": "1", "instruction": "First Instruction - Updated"},
        {"task_id": "2", "instruction": "Second Instruction - Updated"},
        {"task_id": "4", "instruction": "Fourth Instruction"}
    ]
    working_memory.add_or_update_module("TaskList", updated_task_list)

    # Exporting the entire memory
    print(working_memory.export_memory())

