"""Orchestration layer for executing multiple tools.

This module provides high-level orchestration functions that coordinate
multiple tool invocations while maintaining compatibility with the baseline
behavior.
"""

from typing import Any, Callable, Dict, List

from agent_hooks.core import Tool, ToolInvocation, ToolResult, invoke_tool


def invoke_all(
    tools: List[Tool],
    names: List[str],
    payloads: List[Dict[str, Any]]
) -> List[ToolResult]:
    """Execute multiple tools using alternating log styles.
    
    This function orchestrates multiple tool invocations, alternating between
    log style 'a' (even indices) and log style 'b' (odd indices), exactly
    matching the baseline run_all behavior.
    
    Args:
        tools: List of callables to invoke
        names: List of tool names (same length as tools)
        payloads: List of argument dictionaries (same length as tools)
        
    Returns:
        List of ToolResult objects, one per tool invocation
    """
    results: List[ToolResult] = []
    
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        # Alternate between log styles to match baseline behavior
        log_style = "a" if index % 2 == 0 else "b"
        
        invocation = ToolInvocation(
            tool=tool,
            name=name,
            args=args,
            log_style=log_style,
        )
        
        result = invoke_tool(invocation)
        results.append(result)
    
    return results


def invoke_all_as_dicts(
    tools: List[Tool],
    names: List[str],
    payloads: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Execute multiple tools and return baseline-compatible dictionaries.
    
    This is a convenience wrapper around invoke_all that converts all results
    to the baseline dictionary format, providing a drop-in replacement for
    the baseline run_all function.
    
    Args:
        tools: List of callables to invoke
        names: List of tool names (same length as tools)
        payloads: List of argument dictionaries (same length as tools)
        
    Returns:
        List of dictionaries in baseline format
    """
    results = invoke_all(tools, names, payloads)
    return [result.to_dict() for result in results]
