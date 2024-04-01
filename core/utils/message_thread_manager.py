import sqlite3
import json
from typing import List, Dict, Any, Optional
from core.utils.llm import make_llm_api_call
from core.tools.files_tool import FilesTool


class MessageThreadManager:
    def __init__(self, db_path: str = "db.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ThreadMessages
                               (thread_id INTEGER PRIMARY KEY, messages TEXT)''')
        self.conn.commit()

    def create_thread(self) -> int:
        self.cursor.execute("INSERT INTO ThreadMessages (messages) VALUES (?)", (json.dumps([]),))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_message(self, thread_id: int, message_data: Dict[str, Any]):
        try:
            serialized_message_data = json.dumps(message_data)
        except TypeError as e:
            print(f"Error serializing message_data: {e}")
            # Handle non-serializable message_data appropriately here
            # For the sake of demonstration, we'll convert non-serializable objects to a string representation
            message_data = {k: str(v) for k, v in message_data.items()}
            serialized_message_data = json.dumps(message_data)
        
        self.cursor.execute("SELECT messages FROM ThreadMessages WHERE thread_id=?", (thread_id,))
        messages = json.loads(self.cursor.fetchone()[0])
        messages.append(json.loads(serialized_message_data))
        self.cursor.execute("UPDATE ThreadMessages SET messages=? WHERE thread_id=?", (json.dumps(messages), thread_id))
        self.conn.commit()

    def get_message(self, thread_id: int, message_index: int) -> Optional[Dict[str, Any]]:
        self.cursor.execute("SELECT messages FROM ThreadMessages WHERE thread_id=?", (thread_id,))
        messages = json.loads(self.cursor.fetchone()[0])
        if message_index < len(messages):
            return messages[message_index]
        return None

    def modify_message(self, thread_id: int, message_index: int, new_message_data: Dict[str, Any]):
        try:
            serialized_new_message_data = json.dumps(new_message_data)
        except TypeError as e:
            print(f"Error serializing new_message_data: {e}")
            # Handle non-serializable new_message_data appropriately here
            new_message_data = {k: str(v) for k, v in new_message_data.items()}
            serialized_new_message_data = json.dumps(new_message_data)
        
        self.cursor.execute("SELECT messages FROM ThreadMessages WHERE thread_id=?", (thread_id,))
        messages = json.loads(self.cursor.fetchone()[0])
        if message_index < len(messages):
            messages[message_index] = json.loads(serialized_new_message_data)
            self.cursor.execute("UPDATE ThreadMessages SET messages=? WHERE thread_id=?", (json.dumps(messages), thread_id))
            self.conn.commit()

    def remove_message(self, thread_id: int, message_index: int):
        self.cursor.execute("SELECT messages FROM ThreadMessages WHERE thread_id=?", (thread_id,))
        messages = json.loads(self.cursor.fetchone()[0])
        if message_index < len(messages):
            del messages[message_index]
            self.cursor.execute("UPDATE ThreadMessages SET messages=? WHERE thread_id=?", (json.dumps(messages), thread_id))
            self.conn.commit()

    def list_messages(self, thread_id: int) -> List[Dict[str, Any]]:
        self.cursor.execute("SELECT messages FROM ThreadMessages WHERE thread_id=?", (thread_id,))
        messages = json.loads(self.cursor.fetchone()[0])
        return messages

    def run_thread(self, thread_id: int, system_message_data: Dict[str, Any], model_name: Any, json_mode: bool = False, temperature: int = 0, max_tokens: Optional[Any] = None, tools: Optional[List[Dict[str, Any]]] = None, tool_choice: str = "auto") -> Any:
        messages = self.list_messages(thread_id)
        temp_messages = [system_message_data] + messages
        response = make_llm_api_call(temp_messages, model_name, json_mode, temperature, max_tokens, tools, tool_choice)

        if tools is None:
            response_content = response.choices[0].message['content']
            self.add_message(thread_id, {"role": "assistant", "content": response_content})
        else:
            try:
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls
                print("\nLength of tool calls", len(tool_calls))
                print("Tool calls:", tool_calls)  # Logging the tool calls
                if tool_calls:
                    from core.tools.files_tool import FilesTool
                    
                    files_tool_instance = FilesTool()
                    
                    available_functions = {
                        "create_file": files_tool_instance.create_file,
                        "edit_file_contents": files_tool_instance.edit_file_contents,
                        "move_file": files_tool_instance.move_file,
                        "rename_file": files_tool_instance.rename_file,
                        "delete_file": files_tool_instance.delete_file,
                        "get_file_tree": files_tool_instance.get_file_tree,
                        "read_file_contents": files_tool_instance.read_file_contents,
                        "read_directory_contents": files_tool_instance.read_directory_contents,
                    }

                    # Ensure response_message is serializable before adding
                    try:
                        serialized_response_message = json.dumps(response_message)
                        self.add_message(thread_id, json.loads(serialized_response_message))
                    except TypeError as e:
                        print(f"Error serializing response_message: {e}")
                        # Handle non-serializable response_message appropriately here
                
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_to_call = available_functions[function_name]
                        function_args = json.loads(tool_call.function.arguments)
                        print("Function arguments for", function_name, ":", function_args)  # Logging function arguments
                        function_response = function_to_call(**function_args)
                        self.add_message(thread_id, {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        })  # extend conversation with function response
                        print("Messages after appending function response:", self.list_messages(thread_id))  # Logging messages after appending function response
            except AttributeError:
                pass

        response = make_llm_api_call(temp_messages, model_name, json_mode, temperature, max_tokens, tools, tool_choice)
        response_content = response.choices[0].message['content']
        self.add_message(thread_id, {"role": "assistant", "content": response_content})

        return response

if __name__ == "__main__":
    # Initialize the MessageThreadManager with a database path
    manager = MessageThreadManager()
    
    # Create a new thread
    thread_id = manager.create_thread()
    print(f"Created thread with ID: {thread_id}")
    
    tools = []
    tools.extend(FilesTool.schema())

    # # Add messages to the thread
    manager.add_message(thread_id, {"role": "user", "content": "Create multiple random file names with random characters as names"})
    # manager.add_message(thread_id, {"role": "assistant", "content": "I'm fine, thank you. How can I assist you today?"})
    # print("Added initial messages to the thread.")
    
    # # List all messages in the thread
    # messages = manager.list_messages(thread_id)
    # print("Listing all messages in the thread:")
    # for message in messages:
    #     print(message)
    
    # # Modify a message in the thread
    # manager.modify_message(thread_id, 0, {"role": "user", "content": "Hello, how are you doing?"})
    # print("Modified the first message.")
    
    # # Remove a message from the thread
    # manager.remove_message(thread_id, 1)
    # print("Removed the second message from the thread.")
    
    # List messages again to see the changes
    updated_messages = manager.list_messages(thread_id)
    print("Listing all messages after modifications:")
    for message in updated_messages:
        print(message)
    
    # Run a thread simulation with a system message and check for tool calls
    system_message_data = {"role": "system", "content": "Just do what you are told."}
    response = manager.run_thread(thread_id, system_message_data, "gpt-4-turbo-preview", temperature=0.0, tools=tools)
    print("Ran the thread with a system message and processed tool calls.")
    
    # Display the final list of messages after running the thread
    final_messages = manager.list_messages(thread_id)
    print("Final list of messages in the thread:")
    for message in final_messages:
        print(message)
