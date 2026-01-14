"""Enhanced, structured agent tool hook layer.

This module provides a small, well-defined public API that is fully
backwards-compatible (returns the same dict shapes and log messages as the
baseline) while offering a structured representation (`ToolResult`) that is
easier to reason about and extend.

Do not modify `agent_tools_hook_origin.py` — this module builds on top of it.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional

Tool = Callable[..., Any]


@dataclass
class LogRecord:
    """Structured log entry.

    The baseline uses plain strings; we preserve the original string in
    `message` so the baseline representation can be recovered exactly.
    Additional structured fields may be added later without losing the
    original text.
    """
    message: str
    kind: Optional[str] = None


@dataclass
class ToolResult:
    tool_name: str
    status: str
    error: Optional[str]
    args: Dict[str, Any]
    output: Any
    logs: List[LogRecord] = field(default_factory=list)

    def to_baseline_dict(self) -> Dict[str, Any]:
        """Return a plain dict that is semantically identical to the baseline.

        The `logs` value is a list of the original log strings in the same
        order so consumers that expect the baseline shape get identical
        output.
        """
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": [lr.message for lr in self.logs],
        }

    @classmethod
    def from_baseline_dict(cls, d: Dict[str, Any]) -> "ToolResult":
        return cls(
            tool_name=d["tool_name"],
            status=d["status"],
            error=d["error"],
            args=d["args"],
            output=d.get("output"),
            logs=[LogRecord(message=m) for m in d.get("logs", [])],
        )


# Internal helper that centralizes the call/exception/logging behavior.
def _invoke_with_templates(tool: Tool, name: str, args: Dict[str, Any], *, start_msg: str, success_msg: str, failure_msg_fmt: str) -> ToolResult:
    logs: List[LogRecord] = []
    # start message must match baseline formatting (uses repr(args))
    logs.append(LogRecord(message=start_msg))

    status = "ok"
    error: Optional[str] = None
    output: Any = None

    try:
        output = tool(**args)
    except Exception as exc:
        status = "error"
        error = str(exc)
        logs.append(LogRecord(message=failure_msg_fmt.format(exc)))
    else:
        logs.append(LogRecord(message=success_msg))

    return ToolResult(tool_name=name, status=status, error=error, args=args, output=output, logs=logs)


# Public, backward-compatible functions -------------------------------------------------
def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility wrapper that returns the baseline dict shape.

    Internally uses structured types and _invoke_with_templates so the
    implementation is not duplicated.
    """
    start = f"calling {name} with {args!r}"
    tr = _invoke_with_templates(tool, name, args, start_msg=start, success_msg="done", failure_msg_fmt="error: {}")
    return tr.to_baseline_dict()


def call_tool_b(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    start = f"tool {name} start {args!r}"
    tr = _invoke_with_templates(tool, name, args, start_msg=start, success_msg="ok", failure_msg_fmt="failed: {}")
    return tr.to_baseline_dict()


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compatibility orchestration: alternates between A and B (same as
    baseline) but implemented on top of the structured primitives.
    """
    results: List[Dict[str, Any]] = []
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        if index % 2 == 0:
            results.append(call_tool_a(tool, name, args))
        else:
            results.append(call_tool_b(tool, name, args))
    return results


# Structured API for clients who want richer types -------------------------------------
class Runner:
    """Small orchestration class that returns structured `ToolResult`s.

    Example:
        runner = Runner()
        results = runner.run_all_structured([...], [...], [...])
    """

    def call_structured(self, tool: Tool, name: str, args: Dict[str, Any], variant: str = "a") -> ToolResult:
        if variant == "a":
            start = f"calling {name} with {args!r}"
            return _invoke_with_templates(tool, name, args, start_msg=start, success_msg="done", failure_msg_fmt="error: {}")
        elif variant == "b":
            start = f"tool {name} start {args!r}"
            return _invoke_with_templates(tool, name, args, start_msg=start, success_msg="ok", failure_msg_fmt="failed: {}")
        else:
            raise ValueError("unknown variant")

    def run_all_structured(self, tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[ToolResult]:
        results: List[ToolResult] = []
        for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
            variant = "a" if index % 2 == 0 else "b"
            results.append(self.call_structured(tool, name, args, variant=variant))
        return results


__all__ = [
    "ToolResult",
    "LogRecord",
    "call_tool_a",
    "call_tool_b",
    "run_all",
    "Runner",
]
