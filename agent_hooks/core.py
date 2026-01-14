"""Core types and logic for the enhanced agent tool hook layer.

This module defines structured types and centralizes the common logic for
calling tools, handling exceptions, and collecting logs.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


Tool = Callable[..., Any]


@dataclass
class ToolInvocation:
    """Structured representation of a tool invocation request.
    
    Attributes:
        tool: The callable to invoke
        name: Human-readable name for the tool
        args: Keyword arguments to pass to the tool
        log_style: Style variant for log messages ('a' or 'b')
    """
    tool: Tool
    name: str
    args: Dict[str, Any]
    log_style: str = "a"
    
    def __post_init__(self):
        if self.log_style not in ("a", "b"):
            raise ValueError(f"log_style must be 'a' or 'b', got {self.log_style!r}")


@dataclass
class ToolResult:
    """Structured representation of a tool invocation result.
    
    This type provides full compatibility with the baseline dictionary format
    while adding type safety and clarity.
    
    Attributes:
        tool_name: Name of the tool that was invoked
        status: 'ok' if successful, 'error' if an exception occurred
        error: Error message if status is 'error', None otherwise
        args: Arguments that were passed to the tool
        output: Return value from the tool if successful, None otherwise
        logs: List of log messages generated during execution
    """
    tool_name: str
    status: str
    error: Optional[str]
    args: Dict[str, Any]
    output: Any
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to baseline-compatible dictionary format.
        
        Returns:
            A dictionary with exactly the same structure as the baseline
            implementation, ensuring full compatibility.
        """
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": self.logs,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ToolResult":
        """Create a ToolResult from a baseline dictionary.
        
        Args:
            d: Dictionary in baseline format
            
        Returns:
            ToolResult instance with the same data
        """
        return cls(
            tool_name=d["tool_name"],
            status=d["status"],
            error=d["error"],
            args=d["args"],
            output=d["output"],
            logs=d["logs"],
        )


def invoke_tool(invocation: ToolInvocation) -> ToolResult:
    """Execute a single tool and return a structured result.
    
    This function centralizes all the logic for calling a tool, handling
    exceptions, and collecting logs. It supports two log styles ('a' and 'b')
    that match the baseline call_tool_a and call_tool_b implementations.
    
    Args:
        invocation: Structured tool invocation request
        
    Returns:
        ToolResult containing execution details and logs
    """
    result = ToolResult(
        tool_name=invocation.name,
        status="ok",
        error=None,
        args=invocation.args,
        output=None,
        logs=[],
    )
    
    # Generate initial log message based on style
    if invocation.log_style == "a":
        result.logs.append(f"calling {invocation.name} with {invocation.args!r}")
    else:  # style 'b'
        result.logs.append(f"tool {invocation.name} start {invocation.args!r}")
    
    # Execute the tool and handle exceptions
    try:
        output = invocation.tool(**invocation.args)
    except Exception as exc:
        result.status = "error"
        result.error = str(exc)
        # Generate error log message based on style
        if invocation.log_style == "a":
            result.logs.append(f"error: {exc}")
        else:  # style 'b'
            result.logs.append(f"failed: {exc}")
    else:
        result.output = output
        # Generate success log message based on style
        if invocation.log_style == "a":
            result.logs.append("done")
        else:  # style 'b'
            result.logs.append("ok")
    
    return result
