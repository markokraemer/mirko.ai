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

os.getenv("OPENAI_API_KEY")
client = OpenAI()
initialize_logging()



# =========================
# Base Assistant Class
# =========================

class BaseAssistant:
    def __init__(self, name: str, instructions: str, tools: List[Dict] = []):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.assistant_id = self.create_assistant(name, instructions, tools)

    @staticmethod
    def create_assistant(name, instructions, tools=[], model="gpt-4-turbo-preview"):
        
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model
        )
        return assistant.id

    @staticmethod
    def start_new_thread():
        empty_thread = client.beta.threads.create()
        return empty_thread.id

    @staticmethod
    def add_message(thread_id, content, role="user"):
        thread_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
        )
        return thread_message

    @staticmethod
    def run_thread(thread_id, assistant_id):
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        return run.id

    @staticmethod
    def get_run(thread_id, run_id):
        run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
        )
        return run

    @staticmethod
    def get_messages_in_thread(thread_id, stringified=False):
        messages = client.beta.threads.messages.list(thread_id)
        # Sort messages by 'created_at' to ensure they are in the correct order
        sorted_messages = sorted(messages.data, key=lambda x: x.created_at)
        if stringified:
            string_messages = []
            for message in sorted_messages:
                role = message.role.upper()
                # Assuming the first item in content list is the main text
                content = message.content[0].text.value
                string_messages.append(f"{role}: {content}")
            return "\n\n".join(string_messages)
        return sorted_messages

    async def check_run_status_and_execute_action(self, thread_id: str, run_id: str):
        while True:
            run = self.get_run(thread_id, run_id)
            if run.status == "requires_action":
                await self.execute_run_action(run_id, thread_id)
                await asyncio.sleep(3)
            elif run.status in ["in_progress", "queued", "cancelling"]:
                await asyncio.sleep(3)                
            elif run.status in ["completed", "cancelled", "failed", "expired"]:
                break

    async def execute_run_action(self, run_id, thread_id):
        run = BaseAssistant.get_run(thread_id, run_id)
        required_action = run.required_action if run.status == "requires_action" else None
        logging.info(f"Debug: Required action for run_id {run_id} is {required_action}")

        if required_action and required_action.type == "submit_tool_outputs":
            tool_calls = required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            logging.info(f"Debug: Processing {len(tool_calls)} tool calls for submission.")

            # Instantiate TerminalTool and FilesTool without hardcoded arguments
            terminal_tool = TerminalTool()
            files_tool = FilesTool()

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                logging.info(f"Debug: Attempting to execute function {function_name} with arguments {arguments}")

                # Dynamically call the function with the provided arguments
                try:
                    # Attempt to find the function in terminal_tool or files_tool instances
                    function = None
                    for tool_instance in [terminal_tool, files_tool]:
                        if hasattr(tool_instance, function_name):
                            function = getattr(tool_instance, function_name)
                            logging.info(f"Debug: Found function {function_name} in {type(tool_instance).__name__}")
                            break

                    if function:
                        # Execute the function asynchronously if it's a coroutine
                        if inspect.iscoroutinefunction(function):
                            output = await function(**arguments)
                        else:
                            output = function(**arguments)
                        logging.info(f"Debug: Function {function_name} executed successfully with output: {output}")
                        # Extract the output if it's an instance of ToolResult
                        if isinstance(output, ToolResult):
                            output = output.output
                    else:
                        output = "Function not found"
                        logging.info(f"Debug: Function {function_name} not found in TerminalTool or FilesTool instances")
                except Exception as e:
                    output = f"An exception has occurred: {e}"
                    logging.info(f"Debug: Exception occurred while executing function {function_name}: {e}")

                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": str(output)  # Convert output to string to avoid type error
                })

            # Submit the tool outputs
            try:
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
                logging.info(f"Debug: Successfully submitted tool outputs for run_id {run_id}")
            except Exception as e:
                logging.info(f"Failed to submit tool outputs for run_id {run_id}: {e}")

    def generate_next_action(self, thread_id):
        messages_in_thread = self.get_messages_in_thread(thread_id, stringified=True)
        messages = [
            {
                "role": "system",
                "content": """     
    You are the internal monologue of Mirko.ai the Expert AI Software Engineer. 

    Context: Mirko.ai is an advanced AI software engineer, capable of independent problem-solving and decision-making within the realm of software development. Mirko.ai has been assigned with a user objective and is working iteratively to accomplish it.

    As the internal monologue of Mirko.ai, you are reflecting on your current situation and planning your next steps towards achieving the user objective.

    Output a JSON with: 
    - Your observations, thoughts in a tree-of-thoughts, upcoming actions list, next action to conduct.

 """
            },
            {
                "role": "user",
                "content": f""" Event History: {messages_in_thread} 
                Working Memory: 
"""
            },
        ]
        response = make_llm_api_call(messages, model_name="gpt-4-turbo-preview")
        new_message_contents = response.choices[0].message['content']
        self.add_message(thread_id, new_message_contents, role="user")


    def generate_playground_access(self, thread_id):
        playground_url = f'https://platform.openai.com/playground?assistant={self.assistant_id}&mode=assistant&thread={thread_id}'
        logging.info(f'Playground Access URL: {playground_url}')




async def start_session_run(user_request):

    tools = []
    tools.extend(TerminalTool.schema())
    tools.extend(FilesTool.schema())

    instructions = """
    You are Mirko, an expert AI software engineer, a brilliant and meticulous software engineer working iteratively towards implementing the received task from the user. You are an autonomous cognitive digital entity using your tools to interact with your personal Linux workspace.
    
    
    - Generate_task_list
    - Process_task
    - Send_web_browsing_instructions_to_browsing_agent(he reports back)
    - Send_terminal_commands
    - WM: Full Latest Directory Contents in Session, Open Tabs & past interactions, Open Terminal Sessions and most recent log, 
    
    Retrieval:
    - Expand_File_tree
    - Open_File
    - Open_Files_in_Editor
    - Read_directory_contents
    - Read_file_contents

    - Code_snippet_retrieval(query)

    Files:
    - Rename_file(current_file_path, new_file_path)
    - Delete_file(file_path)
    - Move_file(current_file_path, new_file_path)
    - Edit_file_contents(instructions)

    Terminal:
    - New_terminal_session()
    - Close_terminal_session(session_id)
    - Send_terminal_command(session_id, command)
    - get_session_log(session_id, timestamp/other-indicator)

    Browsing:
    - Send_browsing_instructions()


    dissect, think step by step... etc.. – have it as function calls too

    """    

    assistant = BaseAssistant("Mirko.ai", instructions, tools)

    # Initial User Request
    thread_id = assistant.start_new_thread()
    assistant.generate_playground_access(thread_id)
    assistant.add_message(thread_id, user_request, "user")
    # Recursive self-debate Loop
    while True:
        run_id = assistant.run_thread(thread_id, assistant.assistant_id)
        await assistant.check_run_status_and_execute_action(thread_id, run_id)
        assistant.generate_next_action(thread_id)

        # Sample usage of get_messages_in_thread with stringified=True
        stringified_messages = assistant.get_messages_in_thread(thread_id, stringified=True)
        logging.info(f"Stringified message thread {thread_id} for {assistant.name}: {stringified_messages}")


if __name__ == "__main__":

    user_request = "Build a simple Landing Page for my construction company. "        
    asyncio.run(start_session_run(user_request))


