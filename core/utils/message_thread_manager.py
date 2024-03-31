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
                               (index INTEGER, thread_id INTEGER, role TEXT, content TEXT,
                               FOREIGN KEY(thread_id) REFERENCES threads(id),
                               UNIQUE(index, thread_id))''')
        self.conn.commit()

    def create_thread(self) -> int:
        self.cursor.execute("INSERT INTO threads DEFAULT VALUES")
        self.conn.commit()
        return self.cursor.lastrowid

    def add_message(self, thread_id: int, role: str, content: str) -> int:
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be either 'user' or 'assistant'")
        self.cursor.execute("SELECT MAX(index) FROM messages WHERE thread_id=?", (thread_id,))
        max_index = self.cursor.fetchone()[0]
        next_index = (max_index if max_index is not None else -1) + 1
        self.cursor.execute("INSERT INTO messages (index, thread_id, role, content) VALUES (?, ?, ?, ?)",
                            (next_index, thread_id, role, content))
        self.conn.commit()
        return next_index

    def get_message(self, thread_id: int, message_index: int) -> Optional[Dict[str, Any]]:
        self.cursor.execute("SELECT role, content FROM messages WHERE thread_id=? AND index=?", (thread_id, message_index))
        message = self.cursor.fetchone()
        return {"role": message[0], "content": message[1]} if message else None

    def modify_message(self, thread_id: int, message_index: int, content: str):
        self.cursor.execute("UPDATE messages SET content=? WHERE thread_id=? AND index=?", (content, thread_id, message_index))
        self.conn.commit()

    def remove_message(self, thread_id: int, message_index: int):
        self.cursor.execute("DELETE FROM messages WHERE thread_id=? AND index=?", (thread_id, message_index))
        self.conn.commit()

    def list_messages(self, thread_id: int) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT index, role, content FROM messages WHERE thread_id=? ORDER BY index ASC", (thread_id,))
        return [{"index": row[0], "role": row[1], "content": row[2]} for row in self.cursor.fetchall()]

    def run_thread(self, thread_id: int, system_message: str, messages: Any, model_name: Any, json_mode: bool = False, temperature: int = 0, max_tokens: Optional[Any] = None) -> Any:
        from core.utils.llm import make_llm_api_call
        messages = [{"role": "system", "content": system_message}] + self.list_messages(thread_id)
        response = make_llm_api_call(messages, model_name, json_mode, temperature, max_tokens)
        if response:
            response_content = response.choices[0].message['content']
            self.add_message(thread_id, "assistant", response_content)
        return response



