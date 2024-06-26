import json
from dataclasses import dataclass
from pydantic import Field
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from core.tools.base import Tool, ToolResult
from .util import get_b64_screenshot
from .util import get_web_driver, set_web_driver
from .util.highlights import highlight_elements_with_labels
from agency_swarm.util import get_openai_client

@dataclass
class SelectDropdownResult(ToolResult):
    screenshot_path: str = ""
    analysis_text: str = ""

class SelectDropdown(Tool):
    """
    This tool selects an option in a dropdown on the current web page based on the description of that element and which option to select.
    """

    description: str = Field(
        ..., description="Description of which option to select and for which dropdown on the page, clearly stated in natural language.",
        examples=["Select Germany option in the 'Country' dropdown."]
    )

    def run(self) -> SelectDropdownResult:
        wd = get_web_driver()
        client = get_openai_client()
        wd = highlight_elements_with_labels(wd, 'select')
        screenshot = get_b64_screenshot(wd)
        all_elements = wd.find_elements(By.CSS_SELECTOR, '.highlighted-element')

        if len(all_elements) == 0:
            set_web_driver(wd)
            return self.fail_response("This page does not contain any dropdowns. It might be an input element instead. Try using SendKeys function.", 2)

        all_selector_values = {}
        for i, element in enumerate(all_elements):
            select = Select(element)
            options = select.options
            selector_values = {str(j): option.text for j, option in enumerate(options) if j <= 10}
            all_selector_values[str(i + 1)] = selector_values

        messages = [
            {
                "role": "system",
                "content": """You are an advanced web scraping tool designed to interpret and interact with webpage 
screenshots. Users will provide a screenshot where all selector (dropdown) fields are distinctly highlighted in 
red. Each selector will have a sequence number, ranging from 1 to n, displayed near the left side of its border. 
Your task is to analyze the screenshot, identify the selectors based on the user's description, 
and output the sequence numbers of these fields in JSON format, paired with the desired selector index value. For 
instance, if the user's task involves selecting the first option in 2 dropdowns from website, your output should be in the 
format: {"3": "0", "4": "1"}, where 3 and 4 are sequence values, and 0 and 1 are index values from the available options.
If no element on the screenshot matches the user’s description, explain to the user what's on the page, 
and tell him where these elements are most likely to located. 
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
                        "text": f"{self.description} \n\nThese are the possible selector values: {json.dumps(all_selector_values)}",
                    }
                ]
            }

        ]

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1024,
        )

        message_text = response.choices[0].message.content

        if "none" in message_text.lower():
            return self.fail_response("No element found that matches the description. To further analyze the page, use the AnalyzeContent tool.", 3)

        try:
            json_text = json.loads(message_text[message_text.find("{"):message_text.find("}") + 1])
            for key, value in json_text.items():
                element = all_elements[int(key) - 1]
                select = Select(element)
                select.select_by_index(int(value))
            return self.success_response("Success. Option is selected in the dropdown. To further analyze the page, use the AnalyzeContent tool.")
        except Exception as e:
            return self.fail_response(f"Could not set option in this dropdown. Error: {str(e)} To further analyze the page, use the AnalyzeContent tool.", 4)

        finally:
            set_web_driver(wd)
