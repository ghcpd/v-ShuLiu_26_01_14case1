"""Public API for the enhanced agent tool hook layer.

This module provides a clean, high-level interface for tool invocation that
can be used as a drop-in replacement for the baseline implementation while
offering better structure and extensibility.

Example usage:
    >>> from agent_tools_hook import run_all_tools, ToolResult
    >>> 
    >>> def my_tool(x, y):
    ...     return x + y
    >>> 
    >>> results = run_all_tools(
    ...     tools=[my_tool],
    ...     names=["add"],
    ...     payloads=[{"x": 1, "y": 2}]
    ... )
    >>> 
    >>> # Results are structured ToolResult objects
    >>> assert isinstance(results[0], ToolResult)
    >>> assert results[0].output == 3
    >>> 
    >>> # Can convert to baseline dict format
    >>> dicts = [r.to_dict() for r in results]
"""

from typing import Any, Callable, Dict, List

from agent_hooks import ToolInvocation, ToolResult, invoke_all, invoke_tool

__all__ = [
    "ToolInvocation",
    "ToolResult",
    "invoke_single_tool",
    "run_all_tools",
]


def invoke_single_tool(
    tool: Callable[..., Any],
    name: str,
    args: Dict[str, Any],
    log_style: str = "a"
) -> ToolResult:
    """Invoke a single tool with structured result.
    
    This is a convenience wrapper that creates a ToolInvocation and executes it,
    returning a structured ToolResult.
    
    Args:
        tool: The callable to invoke
        name: Human-readable name for the tool
        args: Keyword arguments to pass to the tool
        log_style: Log message style ('a' or 'b')
        
    Returns:
        ToolResult containing execution details and logs
    """
    invocation = ToolInvocation(tool=tool, name=name, args=args, log_style=log_style)
    return invoke_tool(invocation)


def run_all_tools(
    tools: List[Callable[..., Any]],
    names: List[str],
    payloads: List[Dict[str, Any]]
) -> List[ToolResult]:
    """Execute multiple tools with alternating log styles.
    
    This function provides a high-level interface that matches the baseline
    run_all behavior while returning structured ToolResult objects instead
    of plain dictionaries.
    
    Args:
        tools: List of callables to invoke
        names: List of tool names (same length as tools)
        payloads: List of argument dictionaries (same length as tools)
        
    Returns:
        List of ToolResult objects, one per tool invocation
        
    Example:
        >>> def tool_a(x): return x * 2
        >>> def tool_b(y): return y + 10
        >>> 
        >>> results = run_all_tools(
        ...     tools=[tool_a, tool_b],
        ...     names=["double", "add_ten"],
        ...     payloads=[{"x": 5}, {"y": 3}]
        ... )
        >>> 
        >>> assert results[0].output == 10
        >>> assert results[1].output == 13
    """
    return invoke_all(tools, names, payloads)
