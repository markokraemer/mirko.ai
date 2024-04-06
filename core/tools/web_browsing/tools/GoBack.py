from dataclasses import dataclass
from core.tools.base import Tool, ToolResult
import time

from .util.selenium import get_web_driver, set_web_driver

@dataclass
class GoBackResult(ToolResult):
    current_url: str = ""

class GoBack(Tool):
    """
    This tool allows you to go back 1 page in the browser history. Use it in case of a mistake or if a page shows you unexpected content.
    """

    def run(self) -> GoBackResult:
        wd = get_web_driver()

        wd.back()

        time.sleep(3)

        set_web_driver(wd)

        return GoBackResult(success=True, exit_code=0, output="Success. Went back 1 page.", current_url=wd.current_url)
