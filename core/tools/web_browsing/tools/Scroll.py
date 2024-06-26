from typing import Literal
from pydantic import Field
from core.tools.base import Tool, ToolResult
from .util.selenium import get_web_driver, set_web_driver

class ScrollResult(ToolResult):
    message: str = ""

class Scroll(Tool):
    """
    This tool allows you to scroll the current web page up or down by 1 screen height.
    """
    direction: Literal["up", "down"] = Field(
        ..., description="Direction to scroll."
    )

    def run(self) -> ScrollResult:
        wd = get_web_driver()

        height = wd.get_window_size()['height']

        current_scroll_position = wd.execute_script("return window.pageYOffset;")
        total_scroll_height = wd.execute_script("return document.body.scrollHeight;")

        if self.direction == "up":
            if current_scroll_position == 0:
                # Reached the top of the page
                message = "Reached the top of the page. Cannot scroll up any further."
            else:
                wd.execute_script(f"window.scrollBy(0, -{height});")
                message = "Scrolled up by 1 screen height. Make sure to use the AnalyzePage tool to analyze the page after scrolling."

        elif self.direction == "down":
            if current_scroll_position + height >= total_scroll_height:
                # Reached the bottom of the page
                message = "Reached the bottom of the page. Cannot scroll down any further."
            else:
                wd.execute_script(f"window.scrollBy(0, {height});")
                message = "Scrolled down by 1 screen height. Make sure to use the AnalyzePage tool to analyze the page after scrolling."

        set_web_driver(wd)

        return ScrollResult(success=True, exit_code=0, output=message, message=message)
