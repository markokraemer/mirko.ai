import sqlite3
import json

class WorkingMemoryDB:
    def __init__(self, db_path="db.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS working_memory
                               (id INTEGER PRIMARY KEY, topic_name TEXT, data TEXT)''')
        self.conn.commit()

    def add_entry(self, topic_name, data):
        data_json = json.dumps(data)
        self.cursor.execute("INSERT INTO working_memory (topic_name, data) VALUES (?, ?)", (topic_name, data_json))
        self.conn.commit()

    def get_entries(self, topic_name=None):
        if topic_name:
            self.cursor.execute("SELECT data FROM working_memory WHERE topic_name=?", (topic_name,))
        else:
            self.cursor.execute("SELECT data FROM working_memory")
        rows = self.cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

    def update_entry(self, id, new_data):
        new_data_json = json.dumps(new_data)
        self.cursor.execute("UPDATE working_memory SET data=? WHERE id=?", (new_data_json, id))
        self.conn.commit()

    def remove_entry(self, id):
        self.cursor.execute("DELETE FROM working_memory WHERE id=?", (id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


## SAMPLE USAGE EXAMPLE 
if __name__ == "__main__":
    # Initialize the database
    db = WorkingMemoryDB()

    # Example scenario: Managing terminal sessions with a focus on tracking session activity and logging all terminal interactions.
    # This example demonstrates how to store and update terminal session logs, including session activity status and a continuous log of commands and outputs.

    # Adding entries for terminal sessions with detailed logs
    terminal_sessions = [
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
                "2023-03-15T10:02:00 Command: ls -la, Output: total 28\ndrwxr-xr-x 7 user user 4096 Mar 15 10:02 .\ndrwxr-xr-x 3 root root 4096 Mar 14 09:53 ..",
                "2023-03-15T10:10:00 Close_terminal_session: Session 2 closed"
            ]
        }
    ]

    # Storing terminal session logs under the topic "Terminal_Sessions"
    for session in terminal_sessions:
        db.add_entry("Terminal_Sessions", session)

    # Getting all terminal session entries to verify the addition
    all_terminal_sessions = db.get_entries("Terminal_Sessions")
    print("All Terminal Sessions:", all_terminal_sessions)

    # Assuming the entry_id of one of the terminal session logs is known (e.g., 3), updating that session log
    # For example, marking a session as active or adding new entries to the terminal log
    updated_session = {
        "session_id": "2",
        "active": True,
        "terminal_log": [
            "2023-03-15T10:00:00 New_terminal_session: Session 2 started",
            "2023-03-15T10:01:00 Command: pwd, Output: /home/user",
            "2023-03-15T10:02:00 Command: ls -la, Output: total 28\ndrwxr-xr-x 7 user user 4096 Mar 15 10:02 .\ndrwxr-xr-x 3 root root 4096 Mar 14 09:53 ..",
            "2023-03-15T10:03:00 Command: whoami, Output: user",
            "2023-03-15T10:10:00 Close_terminal_session: Session 2 closed"
        ]
    }
    db.update_entry(3, updated_session)

    # Removing a terminal session log, assuming its entry_id is known (e.g., 3)
    db.remove_entry(4)
    db.remove_entry(3)
    db.remove_entry(2)
    db.remove_entry(1)

