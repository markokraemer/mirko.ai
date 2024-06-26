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

    logging.info(f"Making LLM call with model {model_name} and messages: {messages}")

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
                        logging.info(f"LLM call response: {response_content}")
                        return response
                else:
                    logging.info(f"LLM call response: {response_content}")
                    return response
            except OpenAIError as e:
                logging.error(f"API call failed, retrying attempt {attempt + 1}. Error: {e}", exc_info=True)
                time.sleep(5)
            except json.JSONDecodeError:
                logging.error(f"JSON decoding failed, retrying attempt {attempt + 1}", exc_info=True)
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
        logging.info(f"LLM API call parameters set for model {model_name}: {api_call_params}")
        return completion(**api_call_params)

    return attempt_api_call(api_call)



# Sample Usage
if __name__ == "__main__":
    from core.tools import FilesTool
    
    litellm.set_verbose=True
    tools = []
    # tools.extend(TerminalTool.schema())
    tools.extend(FilesTool.schema())

    messages = [{"role": "user", "content": "Create a xxy.txt and read its contents"}]
    model_name = "gpt-4-turbo-preview"
    logging.info(f"Initiating LLM call with model {model_name} and messages: {messages}")
    response = make_llm_api_call(messages, model_name, json_mode=False, temperature=0.5, tools=tools)
    response_message = response.choices[0].message
    logging.info(f"LLM call completed with response: {response_message}")
    