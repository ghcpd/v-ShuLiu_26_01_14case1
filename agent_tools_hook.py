"""Enhanced agent tool hook layer.

This module introduces structured types for tool invocations and results while
preserving the observable behavior of the baseline implementation in
`agent_tools_hook_origin.py`.
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from agent_tools_hook_origin import call_tool_a as origin_call_tool_a, call_tool_b as origin_call_tool_b

Tool = Callable[..., Any]


@dataclass
class ToolResult:
    tool_name: str
    status: str
    error: Optional[str]
    args: Dict[str, Any]
    output: Any
    logs: List[str]

    def to_baseline_dict(self) -> Dict[str, Any]:
        """Return a plain dict in the same shape as the baseline."""
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": list(self.logs),
        }

    @classmethod
    def from_baseline_dict(cls, data: Dict[str, Any]) -> "ToolResult":
        return cls(
            tool_name=data["tool_name"],
            status=data["status"],
            error=data.get("error"),
            args=data["args"],
            output=data.get("output"),
            logs=list(data.get("logs", [])),
        )


def _invoke(tool: Tool, name: str, args: Dict[str, Any], variant: str) -> ToolResult:
    """Centralized invocation logic.

    Variant must be either 'a' or 'b'. The messages are chosen to match the
    baseline implementation exactly so that the produced baseline dicts are
    identical when converted.
    """
    logs: List[str] = []
    if variant == "a":
        logs.append(f"calling {name} with {args!r}")
    elif variant == "b":
        logs.append(f"tool {name} start {args!r}")
    else:
        raise ValueError("unknown variant")

    status = "ok"
    error = None
    output = None

    try:
        output = tool(**args)
    except Exception as exc:  # keep same behavior: capture str(exc)
        status = "error"
        error = str(exc)
        if variant == "a":
            logs.append(f"error: {exc}")
        else:
            logs.append(f"failed: {exc}")
    else:
        output = output
        if variant == "a":
            logs.append("done")
        else:
            logs.append("ok")

    return ToolResult(tool_name=name, status=status, error=error, args=args, output=output, logs=logs)


def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
    """Call a tool using the 'a' variant and return a structured result."""
    return _invoke(tool, name, args, variant="a")


def call_tool_b(tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
    """Call a tool using the 'b' variant and return a structured result."""
    return _invoke(tool, name, args, variant="b")


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[ToolResult]:
    """Orchestrate calls, alternating between the two variants (a, b, a...).

    The order and number of underlying tool calls mirror the baseline
    implementation exactly. The function returns a list of structured
    `ToolResult` objects. Use `ToolResult.to_baseline_dict()` to obtain
    plain dictionaries compatible with the baseline.
    """
    results: List[ToolResult] = []
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        if index % 2 == 0:
            results.append(call_tool_a(tool, name, args))
        else:
            results.append(call_tool_b(tool, name, args))
    return results


__all__ = ["ToolResult", "call_tool_a", "call_tool_b", "run_all"]
