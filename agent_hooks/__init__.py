"""Enhanced agent tool hook layer with structured types and clean abstractions.

This package provides a cleaner, more maintainable implementation of the agent
tool hook functionality. It introduces:

- Structured types (dataclasses) for invocations, results, and logs
- Centralized tool execution logic
- Clear separation between orchestration and implementation details
- Full compatibility with the baseline behavior

Public API:
    ToolInvocation: Structured representation of a tool call
    ToolResult: Structured result with full type safety
    invoke_tool: Core function for executing a single tool
    invoke_all: Orchestrator for multiple tool calls
"""

from agent_hooks.core import ToolInvocation, ToolResult, invoke_tool
from agent_hooks.orchestrator import invoke_all

__all__ = ["ToolInvocation", "ToolResult", "invoke_tool", "invoke_all"]
