import base64
import time
from dataclasses import dataclass
from core.tools.base import Tool, ToolResult
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located, \
    frame_to_be_available_and_switch_to_it
from selenium.webdriver.support.wait import WebDriverWait
from .util import get_b64_screenshot, remove_highlight_and_labels
from .util.selenium import get_web_driver
from agency_swarm.util import get_openai_client

@dataclass
class SolveCaptchaResult(ToolResult):
    attempts: int = 0

class SolveCaptcha(Tool):
    """
    This tool asks a human to solve captcha on the current webpage. Make sure that captcha is visible before running it.
    """

    def run(self) -> SolveCaptchaResult:
        wd = get_web_driver()
        attempts = 0

        try:
            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']"))
            )

            element = WebDriverWait(wd, 3).until(
                presence_of_element_located((By.ID, "recaptcha-anchor"))
            )
        except Exception as e:
            return self.fail_response("Could not find captcha checkbox", 2)

        element.click()

        try:
            # Now check if the reCAPTCHA is checked
            WebDriverWait(wd, 3).until(
                lambda d: d.find_element(By.CLASS_NAME, "recaptcha-checkbox").get_attribute(
                    "aria-checked") == "true"
            )

            return self.success_response("Success")
        except Exception as e:
            pass

        wd.switch_to.default_content()

        client = get_openai_client()

        WebDriverWait(wd, 10).until(
            frame_to_be_available_and_switch_to_it(
                (By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']"))
        )

        time.sleep(2)

        while attempts < 5:
            tiles = wd.find_elements(By.CLASS_NAME, "rc-imageselect-tile")
            tiles = [tile for tile in tiles if
                     not tile.get_attribute("class").endswith("rc-imageselect-dynamic-selected")]

            image_content = []
            i = 0
            for tile in tiles:
                i += 1
                screenshot = get_b64_screenshot(wd, tile)
                image_content.append(
                    {
                        "type": "text",
                        "text": f"Image {i}:",
                    }
                )
                image_content.append(
                    {
                        "type": "image_url",
                        "image_url":
                            {
                                "url": f"data:image/png;base64,{screenshot}",
                                "detail": "high",
                            }
                    },
                )

            task_text = wd.find_element(By.CLASS_NAME, "rc-imageselect-instructions").text.strip().replace("\n", " ")
            continuous_task = 'once there are none left' in task_text.lower()

            task_text = task_text.replace("Click verify", "Output 0")
            task_text = task_text.replace("click skip", "Output 0")
            task_text = task_text.replace("once", "if")
            task_text = task_text.replace("none left", "none")
            task_text = task_text.replace("all", "only")
            task_text = task_text.replace("squares", "images")

            additional_info = ""
            if len(tiles) > 9:
                additional_info = ("Keep in mind that all images are a part of a bigger image "
                                   "from left to right, and top to bottom. The grid is 4x4. ")

            messages = [
                {
                    "role": "system",
                    "content": f"""You are an advanced AI designed to support users with visual impairments. 
                    User will provide you with {i} images numbered from 1 to {i}. Your task is to output 
                    the numbers of the images that contain the requested object, or at least some part of the requested 
                    object. {additional_info}If there are no individual images that satisfy this condition, output 0.
                    """.replace("\n", ""),
                },
                {
                    "role": "user",
                    "content": [
                        *image_content,
                        {
                            "type": "text",
                            "text": f"{task_text}. Only output numbers separated by commas and nothing else. "
                                    f"Output 0 if there are none."
                        }
                    ]
                }]

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1024,
                temperature=0.0,
            )

            message = response.choices[0].message
            message_text = message.content

            if "0" in message_text and "10" not in message_text:
                verify_button = wd.find_element(By.ID, "recaptcha-verify-button")
                verify_button.click()
                time.sleep(1)

                try:
                    if self.verify_checkbox(wd):
                        return self.success_response("Success. Captcha solved.")
                except Exception as e:
                    print('Not checked')
                    pass

            else:
                numbers = [int(s.strip()) for s in message_text.split(",") if s.strip().isdigit()]
                for number in numbers:
                    tiles[number - 1].click()
                    time.sleep(0.5)

                time.sleep(3)

                if not continuous_task:
                    verify_button = wd.find_element(By.ID, "recaptcha-verify-button")
                    verify_button.click()

                    try:
                        if self.verify_checkbox(wd):
                            return self.success_response("Success. Captcha solved.")
                    except Exception as e:
                        pass
                else:
                    continue

            attempts += 1

        wd = remove_highlight_and_labels(wd)
        wd.switch_to.default_content()

        return self.fail_response("Could not solve captcha.", 3)

    def verify_checkbox(self, wd) -> bool:
        wd.switch_to.default_content()

        try:
            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']"))
            )

            WebDriverWait(wd, 5).until(
                lambda d: d.find_element(By.CLASS_NAME, "recaptcha-checkbox").get_attribute(
                    "aria-checked") == "true"
            )

            return True
        except Exception as e:
            wd.switch_to.default_content()

            WebDriverWait(wd, 10).until(
                frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']"))
            )

        return False
