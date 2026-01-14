"""Enhanced agent tool hook layer.

This module provides structured types and a small orchestration API that
preserves the observable behaviour of the baseline `agent_tools_hook_origin.py`.

Key ideas:
- `ToolResult` is a typed, dataclass wrapper around the baseline result
  dictionary but can be converted back exactly via `to_dict()`.
- A centralized `_call_tool` function implements the common logic; it is
  configured by the message templates so both `call_tool_a` and `call_tool_b`
  reproduce the original log messages and error handling.
- `run_all` mirrors the baseline orchestration but returns `ToolResult`
  instances (which can be converted back to baseline dicts).
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

Tool = Callable[..., Any]


@dataclass
class ToolResult:
    """Structured representation of a tool invocation result.

    The instance preserves all information produced by the baseline and
    can be converted back to the original plain-dict form via `to_dict()`.
    """
    tool_name: str
    status: str
    error: Optional[str]
    args: Dict[str, Any]
    output: Any
    logs: List[str] = field(default_factory=list)
    # Additional structured metadata may be stored here without changing
    # baseline semantics; `to_dict()` will still return the original shape.
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict compatible with the baseline result shape."""
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": list(self.logs),
        }


def _call_tool(tool: Tool, name: str, args: Dict[str, Any], *,
               start_msg: str, success_msg: str, error_prefix: str) -> ToolResult:
    """Centralized implementation for calling a tool and collecting logs.

    The three template strings control the exact messages appended to the
    `logs` list so we can reproduce the two baseline variants while avoiding
    code duplication.
    """
    logs: List[str] = []
    # The templates are formatted exactly as in the baseline so ordering and
    # message text remain identical.
    logs.append(start_msg.format(name=name, args=args))

    status = "ok"
    error_str: Optional[str] = None
    output = None

    try:
        output = tool(**args)
    except Exception as exc:  # keep behaviour compatible with baseline
        status = "error"
        error_str = str(exc)
        logs.append(f"{error_prefix}{exc}")
    else:
        logs.append(success_msg)

    return ToolResult(
        tool_name=name,
        status=status,
        error=error_str,
        args=args,
        output=output,
        logs=logs,
    )


def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
    """Enhanced counterpart to `call_tool_a` in the baseline.

    Returns a `ToolResult` but can be converted to the baseline dict with
    `ToolResult.to_dict()` (which preserves the exact `logs` messages).
    """
    return _call_tool(
        tool,
        name,
        args,
        start_msg="calling {name} with {args!r}",
        success_msg="done",
        error_prefix="error: ",
    )


def call_tool_b(tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
    """Enhanced counterpart to `call_tool_b` in the baseline."""
    return _call_tool(
        tool,
        name,
        args,
        start_msg="tool {name} start {args!r}",
        success_msg="ok",
        error_prefix="failed: ",
    )


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[ToolResult]:
    """Orchestrator that mirrors the baseline `run_all` behaviour.

    It alternates between `call_tool_a` and `call_tool_b` just like the
    baseline. The returned list contains `ToolResult` instances; call
    `ToolResult.to_dict()` on each element to obtain the original dict.
    """
    results: List[ToolResult] = []
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        if index % 2 == 0:
            results.append(call_tool_a(tool, name, args))
        else:
            results.append(call_tool_b(tool, name, args))
    return results


def to_baseline_dicts(results: List[ToolResult]) -> List[Dict[str, Any]]:
    """Convert a list of `ToolResult` objects into baseline-compatible dicts."""
    return [r.to_dict() for r in results]
