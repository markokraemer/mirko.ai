from dataclasses import dataclass
from abc import ABC, abstractmethod
import json


@dataclass
class ToolResult:
    success: bool
    exit_code: int
    output: str

class Tool(ABC):
    @abstractmethod
    def schema(self) -> list[dict]:
        pass

    def success_response(self, data: dict | str) -> ToolResult:
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, indent=2)
        return ToolResult(success=True, exit_code=0, output=text)

    def fail_response(self, msg: str, code: int = 1) -> ToolResult:
        return ToolResult(success=False, exit_code=code, output=msg)



