from typing import Any, Callable, Dict, List, Literal
from dataclasses import dataclass


Tool = Callable[..., Any]


@dataclass
class ToolResult:
    tool_name: str
    status: str
    error: str | None
    args: Dict[str, Any]
    output: Any
    logs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": self.logs,
        }


def call_tool(variant: Literal['a', 'b'], tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
    result = ToolResult(
        tool_name=name,
        status="ok",
        error=None,
        args=args,
        output=None,
        logs=[],
    )

    if variant == 'a':
        result.logs.append(f"calling {name} with {args!r}")
    else:
        result.logs.append(f"tool {name} start {args!r}")

    try:
        output = tool(**args)
    except Exception as exc:
        result.status = "error"
        result.error = str(exc)
        if variant == 'a':
            result.logs.append(f"error: {exc}")
        else:
            result.logs.append(f"failed: {exc}")
    else:
        result.output = output
        if variant == 'a':
            result.logs.append("done")
        else:
            result.logs.append("ok")

    return result


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        variant = 'a' if index % 2 == 0 else 'b'
        result = call_tool(variant, tool, name, args)
        results.append(result.to_dict())
    return results