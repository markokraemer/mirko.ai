from typing import List, Dict
import os
from openai import OpenAI
import time
import json
import inspect
import asyncio
import logging

from core.tools import TerminalTool, FilesTool, ToolResult
from core.utils.llm import make_llm_api_call
from core.utils.debug_logging import initialize_logging
from core.memory.working_memory import WorkingMemory  # Import WorkingMemory
from core.message_thread_manager import MessageThreadManager  # Import MessageThreadManager

os.getenv("OPENAI_API_KEY")
client = OpenAI()
initialize_logging()
working_memory = WorkingMemory()  # Initialize WorkingMemory instance
message_thread_manager = MessageThreadManager()  # Initialize MessageThreadManager instance



# =========================
# Assistant Functions
# =========================

def generate_next_action(thread_id):
    messages_in_thread = message_thread_manager.list_messages(thread_id)
    stringified_messages = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages_in_thread])
    # Include working memory in the user message
    messages = [
        {
            "role": "system",
            "content": """     
You are the internal monologue of Mirko.ai the Expert AI Software Engineer. Self-critique and self-debate, make recommendations for the next action - think step by step. 


Mirko is an expert AI software engineer, a brilliant and meticulous software engineer working iteratively towards implementing the received task from the user. You are an autonomous cognitive digital entity using your tools to interact with your personal Linux workspace.

Retrieval:
- Read_directory_contents ! DO THIS AS YOUR FIRST TOOL FUNCTION CALL --> TO GET THE WHOLE CONTENTS OF THE DIRECTORY

Plan: Then plan out the changes you have to do to the directory

Files: Then do any necessary file modifications.
- Edit_file_contents(instructions) 
- Create_file(file_path)
- delete_file(file_path)

"""
        },
        {
            "role": "user",
            "content": f""" Event History: {stringified_messages} """
        },
    ]
    response = make_llm_api_call(messages, model_name="gpt-4-turbo-preview")
    new_message_contents = response.choices[0].message['content']
    message_thread_manager.add_message(thread_id, {"role": "user", "content": new_message_contents})


async def start_session_run(user_request):

    tools = []
    tools.extend(FilesTool.schema())

    instructions = """
You are Mirko, an expert AI software engineer, a brilliant and meticulous software engineer working iteratively towards implementing the received task from the user. You are an autonomous cognitive digital entity using your tools to interact with your personal Linux workspace.

Retrieval:
- Read_directory_contents ! DO THIS AS YOUR FIRST TOOL FUNCTION CALL --> TO GET THE WHOLE CONTENTS OF THE DIRECTORY

Plan: 
- Then plan out the changes you have to do to the directory

Files: Then do any necessary file modifications.
- Edit_file_contents(instructions) 
- Create_file(file_path)
- delete_file(file_path)


Think step by step and logically dissect.
"""    

    thread_id = message_thread_manager.create_thread()
    message_thread_manager.add_message(thread_id, {"role": "user", "content": user_request})
    generate_next_action(thread_id)

    # Recursive self-debate Loop
    while True:
        system_message = {"role": "system", "content": instructions}
        message_thread_manager.run_thread(thread_id, system_message, "gpt-4-turbo-preview", tools=tools)
        generate_next_action(thread_id)

        # Sample usage of get_messages_in_thread with stringified=True
        stringified_messages = message_thread_manager.list_messages(thread_id)
        logging.info(f"Stringified message thread {thread_id} for Mirko.ai: {stringified_messages}")


if __name__ == "__main__":

    user_request = "Make an Mirko.ai Landing page – your own personal landing page about the AI Software Engineer."        
    asyncio.run(start_session_run(user_request))



