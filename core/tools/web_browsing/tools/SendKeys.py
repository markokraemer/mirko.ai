import json
import time
from dataclasses import dataclass
from core.tools.base import Tool, ToolResult
from pydantic import Field
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from .util import get_b64_screenshot
from .util import get_web_driver, set_web_driver
from .util.highlights import highlight_elements_with_labels
from agency_swarm.util import get_openai_client

@dataclass
class SendKeysResult(ToolResult):
    current_url: str = ""

class SendKeys(Tool):
    """
    This tool sends keys into input fields on the current webpage based on the description of that element and what needs to be typed. It then clicks "Enter" on the last element to submit the form. You do not need to tell it to press "Enter"; it will do that automatically.
    """

    description: str = Field(
        ..., description="Description of the inputs to send to the web page, clearly stated in natural language.",
        examples=["Type 'hello' into the 'Search' input field.",
                  "Type johndoe@gmail.com into the 'Email' input field, and type 'password123' into the 'Password' input field.",
                  "Select the second option in the 'Country' dropdown."]
    )

    def run(self) -> SendKeysResult:
        wd = get_web_driver()

        client = get_openai_client()

        wd = highlight_elements_with_labels(wd, 'input, textarea')

        screenshot = get_b64_screenshot(wd)

        all_elements = wd.find_elements(By.CSS_SELECTOR, '.highlighted-element')

        all_element_texts = [element.text for element in all_elements]

        element_texts_json = {}
        for i, element_text in enumerate(all_element_texts):
            element_texts_json[str(i+1)] = element_text

        element_texts_json = json.dumps(element_texts_json)

        messages = [
            {
                "role": "system",
                "content": """You are an advanced web scraping tool designed to interpret and interact with webpage 
screenshots. Users will provide a screenshot where all input fields are distinctly highlighted in 
red. Each input field will have a sequence number, ranging from 1 to n, displayed near the left side of its border. 
Your task is to analyze the screenshot, identify the input fields based on the user's description, 
and output the sequence numbers of these fields in JSON format, paired with the specified text. For 
instance, if the user's task involves entering an email and password, your output should be in the 
format: {"52": "johndoe@gmail.com", "53": "password123"}, where 52 and 53 are sequence numbers of the input fields. 
The enter key will be pressed on the last element automatically.
If no element on the screenshot matches the user’s description, explain to the user what's on the page instead, 
and tell him where these elements are most likely to be located. 
In instances where the label of a clickable element is not visible or discernible 
in the screenshot, you are equipped to infer its sequence number by analyzing its position within the 
DOM structure of the page.""".replace("\n", ""),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{screenshot}",
                    },
                    {
                        "type": "text",
                        "text": f"{self.description} \n\nText on all visible input fields: {element_texts_json}",
                    }
                ]
            }

        ]

        result = None
        error_count = 0
        while True:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1024,
            )

            message = response.choices[0].message
            message_text = message.content

            if "none" in message_text.lower():
                return self.fail_response("No element found that matches the description. To further analyze the page, use the AnalyzeContent tool.", 2)

            try:
                json_text = json.loads(message_text[message_text.find("{"):message_text.find("}") + 1])
            except json.decoder.JSONDecodeError:
                if error_count > 3:
                    return self.fail_response("Could not interpret the response after multiple attempts. To further analyze the page, use the AnalyzeContent tool.", 3)
                error_count += 1
                continue

            try:
                for i, (key, value) in enumerate(json_text.items()):
                    key = int(key)
                    element = all_elements[key - 1]

                    try:
                        element.click()
                        element.send_keys(Keys.CONTROL + "a")  # Select all text in input
                        element.send_keys(Keys.DELETE)
                        element.clear()
                    except Exception:
                        pass
                    element.send_keys(value)
                    # send enter key to the last element
                    if i == len(json_text) - 1:
                        element.send_keys(Keys.RETURN)
                        time.sleep(3)
                break
            except Exception as e:
                message = str(e)[:str(e).find("Stacktrace:")]
                if error_count > 3:
                    return self.fail_response(f"Could not send keys to element. Error: {message} To further analyze the page, use the AnalyzeContent tool.", 4)
                error_count += 1

        set_web_driver(wd)

        return SendKeysResult(success=True, exit_code=0, output=f"Sent input to element and pressed Enter. Current URL is {wd.current_url}", current_url=wd.current_url)
