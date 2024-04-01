import litellm
from litellm import completion
import os
import json
import logging
import openai
from openai import OpenAIError
import time
import logging

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


## Models
# Anthropic models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# OpenAI models: gpt-4-turbo-preview, gpt-4-vision-preview, gpt-4, gpt-3.5-turbo


def make_llm_api_call(messages, model_name, json_mode=False, temperature=0, max_tokens=None, tools=None, tool_choice="auto"):

    litellm.set_verbose=True

    def attempt_api_call(api_call_func, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                response = api_call_func()
                response_content = response.choices[0].message['content'] if json_mode else response
                if json_mode:
                    if not json.loads(response_content):
                        logging.info(f"Invalid JSON received, retrying attempt {attempt + 1}")
                        continue
                    else:
                        return response
                else:
                    return response
            except OpenAIError as e:
                logging.info(f"API call failed, retrying attempt {attempt + 1}. Error: {e}")
                time.sleep(5)
            except json.JSONDecodeError:
                logging.error(f"JSON decoding failed, retrying attempt {attempt + 1}")
                time.sleep(5)
        raise Exception("Failed to make API call after multiple attempts.")

    def api_call():
        api_call_params = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"} if json_mode else None,
            **({"max_tokens": max_tokens} if max_tokens is not None else {})
        }
        if tools:
            api_call_params["tools"] = tools
            api_call_params["tool_choice"] = tool_choice
        return completion(**api_call_params)

    return attempt_api_call(api_call)


def execute_tool_calls(tool_calls):
    from core.tools.files_tool import FilesTool
    files_tool_instance = FilesTool()
    
    function_map = {
        "create_file": files_tool_instance.create_file,
        "edit_file_contents": files_tool_instance.edit_file_contents,
        "move_file": files_tool_instance.move_file,
        "rename_file": files_tool_instance.rename_file,
        "delete_file": files_tool_instance.delete_file,
        "get_file_tree": files_tool_instance.get_file_tree,
        "read_file_contents": files_tool_instance.read_file_contents,
        "read_directory_contents": files_tool_instance.read_directory_contents,
    }
    
    results = []
    for tool_call in tool_calls:
        print(f"\nExecuting tool call\n{tool_call}")
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        if function_name in function_map:
            try:
                result = function_map[function_name](**arguments)
                function_response = {"output": result.output, "success": result.success}
                print(f"Result from tool call\n{function_response}\n")
                results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            except Exception as e:
                error_response = {"error": str(e), "success": False}
                print(f"Result from tool call\n{error_response}\n")
                results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": error_response,
                })
        else:
            error_response = {"error": "Function not found", "success": False}
            print(f"Result from tool call\n{error_response}\n")
            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": error_response,
            })
    
    return results


# Sample Usage
if __name__ == "__main__":
    from core.tools import TerminalTool, FilesTool, ToolResult
    import inspect
    
    litellm.set_verbose=True
    tools = []
    # tools.extend(TerminalTool.schema())
    tools.extend(FilesTool.schema())

    messages = [{"role": "user", "content": "Create a xxy.txt and read its contents"}]
    model_name = "gpt-4-turbo-preview"
    response = make_llm_api_call(messages, model_name, json_mode=False, temperature=0.5, tools=tools)
    response_message = response.choices[0].message
    
    tool_calls = response.choices[0].message.tool_calls

    result = execute_tool_calls(tool_calls)
    print(result)
    # if tool_calls:
    #     print(tool_calls)
    #     # Implement Tool Call Logic
    #     pass

