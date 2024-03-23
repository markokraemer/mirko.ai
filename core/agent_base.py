from typing import List, Dict
import os
from openai import OpenAI
import time
import json
import inspect
import asyncio

from core.tools import TerminalTool, RetrievalTool, ToolResult

os.getenv("OPENAI_API_KEY")
client = OpenAI()

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
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status != 'in_progress':
                break
            time.sleep(1)  # Wait for 1 second before checking the status again
        return run

    @staticmethod
    def get_messages_in_thread(thread_id):
        messages = client.beta.threads.messages.list(thread_id)
        return messages

    def generate_playground_access(self, thread_id):
        playground_url = f'https://platform.openai.com/playground?assistant={self.assistant_id}&mode=assistant&thread={thread_id}'
        print(f'Playground Access URL: {playground_url}')


    @staticmethod
    async def execute_run_action(run_id, thread_id):
        run = BaseAssistant.get_run(thread_id, run_id)
        required_action = run.required_action if run.status == "requires_action" else None
        print(f"Debug: Required action for run_id {run_id} is {required_action}")

        if required_action and required_action.type == "submit_tool_outputs":
            tool_calls = required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            print(f"Debug: Processing {len(tool_calls)} tool calls for submission.")

            # Instantiate TerminalTool and RetrievalTool without hardcoded arguments
            terminal_tool = TerminalTool()
            retrieval_tool = RetrievalTool()

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print(f"Debug: Attempting to execute function {function_name} with arguments {arguments}")

                # Dynamically call the function with the provided arguments
                try:
                    # Attempt to find the function in terminal_tool or retrieval_tool instances
                    function = None
                    for tool_instance in [terminal_tool, retrieval_tool]:
                        if hasattr(tool_instance, function_name):
                            function = getattr(tool_instance, function_name)
                            print(f"Debug: Found function {function_name} in {type(tool_instance).__name__}")
                            break

                    if function:
                        # Execute the function asynchronously if it's a coroutine
                        if inspect.iscoroutinefunction(function):
                            output = await function(**arguments)
                        else:
                            output = function(**arguments)
                        print(f"Debug: Function {function_name} executed successfully with output: {output}")
                        # Extract the output if it's an instance of ToolResult
                        if isinstance(output, ToolResult):
                            output = output.output
                    else:
                        output = "Function not found"
                        print(f"Debug: Function {function_name} not found in TerminalTool or RetrievalTool instances")
                except Exception as e:
                    output = f"An exception has occurred: {e}"
                    print(f"Debug: Exception occurred while executing function {function_name}: {e}")

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
                print(f"Debug: Successfully submitted tool outputs for run_id {run_id}")
            except Exception as e:
                print(f"Failed to submit tool outputs for run_id {run_id}: {e}")





# =========================
# Sequential Process Implementation
# =========================

def initialise_assistants():
    tools = []
    tools.extend(TerminalTool.schema())
    tools.extend(RetrievalTool.schema())
        
    planner_assistant = BaseAssistant("Planner", "You are an Expert Planner.", tools)
    planner_debate_assistant = BaseAssistant("Planner Internal Self", "You are the eval/analysis/debate of the Expert Planner. The internal monologue.", tools)

    return planner_assistant, planner_debate_assistant


# Planner
# - Retrieve code snippets
# - Create_task_list

# Control/Validate
# - Select_task

# Execution 
# - Create_task_implementation_plan
# - Generate_code_new_file_contents
# - create_e2e_browsing_test_instructions
# - Run_e2e_browsing_test
# - run_terminal_command




async def execute_sequential_process(content):
    assistant = initialise_assistants()
    thread_id = assistant.start_new_thread()
    assistant.add_message(thread_id, content, "user")
    run_id = assistant.run_thread(thread_id, assistant.assistant_id)
    run_details = assistant.get_run(thread_id, run_id)
    print(f"Run details for {assistant.name}: {run_details}")
    if run_details.status == 'requires_action':
        await assistant.execute_run_action(run_id, thread_id)
        messages = assistant.get_messages_in_thread(thread_id)
    elif run_details.status != 'in_progress':
        messages = assistant.get_messages_in_thread(thread_id)
    print(f"Message thread {thread_id} for {assistant.name}: {messages}")

    # Generate and print the playground access URL at the end of the sequential process
    assistant.generate_playground_access(thread_id)

if __name__ == "__main__":
    content = "Create multiple files. Then get the file tree."
    asyncio.run(execute_sequential_process(content))
