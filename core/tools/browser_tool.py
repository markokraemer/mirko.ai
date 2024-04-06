from selenium import webdriver
from selenium.webdriver.common.by import By
from core.memory.working_memory import WorkingMemory
from .base import Tool, ToolResult
import time

class BrowserTool(Tool):
    def __init__(self):
        """
        Initializes the BrowserTool with specific Chrome webdriver options.
        """
        # Initialize the webdriver options as in the provided context
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1200x600')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--remote-debugging-port=9222')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def check_browser_tab_for_error(self, full_page_url):
        """
        Checks for errors in a browser tab by loading a URL and inspecting browser logs and page content.

        Args:
            full_page_url (str): The URL of the page to check for errors.

        Returns:
            ToolResult: A ToolResult object indicating whether errors were found, along with the error details.
        """
        driver = webdriver.Chrome(options=self.options)
        driver.get(full_page_url)
        time.sleep(6)  # Wait for the page to load
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']  # Filter out 'SEVERE' level logs as errors

        # Attempt to read the page content for visible error messages
        try:
            page_content = driver.find_element(By.TAG_NAME, 'body').text
            if "Error" in page_content:
                errors.append({'level': 'SEVERE', 'message': page_content, 'source': 'page-content'})
        except Exception as e:
            errors.append({'level': 'SEVERE', 'message': f"Failed to read page content: {str(e)}", 'source': 'page-content'})

        driver.quit()  # Ensure the driver is quit after operation
        if errors:
            return ToolResult(success=True, output=errors, exit_code=0)
        else:
            return ToolResult(success=False, output="No errors found.", exit_code=1)

    @staticmethod
    def schema() -> list[dict]:
        """
        Returns the OpenAPI JSON schema for function calls in the Browser Tool.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": BrowserTool.check_browser_tab_for_error.__name__,
                    "description": BrowserTool.check_browser_tab_for_error.__doc__,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "full_page_url": {
                                "type": "string",
                                "description": "The full URL of the page to check for errors.",
                            }
                        },
                        "required": ["full_page_url"],
                    },
                },
            },
        ]

# Example usage
if __name__ == "__main__":
    browser_tool = BrowserTool()
    errors = browser_tool.check_browser_tab_for_error("https://www.youtube.com/watch?v=LLxWakCWUAI")
    if errors.success:
        print("Errors found:")
        for error in errors.output:
            print(error)
    else:
        print("No errors found.")

