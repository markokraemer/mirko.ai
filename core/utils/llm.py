import litellm
from litellm import completion
import os
import json
import logging
import openai
from openai import OpenAIError
import time
from core.utils.debug_logging import initialize_logging
import logging

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


## Models
# Anthropic models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# OpenAI models: gpt-4-turbo-preview, gpt-4-vision-preview, gpt-4, gpt-3.5-turbo

def make_llm_api_call(messages, model_name, json_mode=False, temperature=0, max_tokens=None):

    # litellm.set_verbose=True

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
        return completion(
            model=model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None,
            **({"max_tokens": max_tokens} if max_tokens is not None else {})
        )

    return attempt_api_call(api_call)



# Sample Usage
if __name__ == "__main__":
    litellm.set_verbose=True
    messages = [{"role": "user", "content": "Tell me a joke. Output a JSON containing the Joke."}]
    model_name = "claude-3-haiku-20240307"
    response = make_llm_api_call(messages, model_name, json_mode=False, temperature=0.5, max_tokens=50)
    print(response)
    
