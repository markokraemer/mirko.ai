import sqlite3
from typing import List, Dict, Any, Optional

class MessageThreadManager:
    def __init__(self, db_path: str = "db.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS threads
                               (id INTEGER PRIMARY KEY)''')  
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                               (id INTEGER PRIMARY KEY, thread_id INTEGER, role TEXT, content TEXT,
                               FOREIGN KEY(thread_id) REFERENCES threads(id))''')
        self.conn.commit()

    def create_thread(self) -> int:
        self.cursor.execute("INSERT INTO threads DEFAULT VALUES")
        self.conn.commit()
        return self.cursor.lastrowid

    def add_message(self, thread_id: int, role: str, content: str) -> int:
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be either 'user' or 'assistant'")
        self.cursor.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
                            (thread_id, role, content))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_message(self, message_id: int) -> Dict[str, Any]:
        self.cursor.execute("SELECT role, content FROM messages WHERE id=?", (message_id,))
        message = self.cursor.fetchone()
        return {"role": message[0], "content": message[1]} if message else None

    def modify_message(self, message_id: int, content: str):
        self.cursor.execute("UPDATE messages SET content=? WHERE id=?", (content, message_id))
        self.conn.commit()

    def remove_message(self, message_id: int):
        self.cursor.execute("DELETE FROM messages WHERE id=?", (message_id,))
        self.conn.commit()

    def list_messages(self, thread_id: int) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT id, thread_id, role, content FROM messages WHERE thread_id=?", (thread_id,))
        messages = []
        for row in self.cursor.fetchall():
            message = {
                "role": row[2],
                "content": row[3]
            }
            if row[2] == "user" or row[2] == "assistant":
                messages.append(message)
        return messages

    def run_thread(self, thread_id: int, system_message: str, messages: Any, model_name: Any, json_mode: bool = False, temperature: int = 0, max_tokens: Optional[Any] = None) -> Any:
        from core.utils.llm import make_llm_api_call
        messages = [{"role": "system", "content": system_message}] + self.list_messages(thread_id)
        response = make_llm_api_call(messages, model_name, json_mode, temperature, max_tokens)
        if response:
            response_content = response.choices[0].message['content']
            self.add_message(thread_id, "assistant", response_content)
        return response



