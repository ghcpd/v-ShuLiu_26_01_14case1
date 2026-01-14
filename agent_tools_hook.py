"""Enhanced agent tool hook layer with clear types and centralized logic.

This module provides a refactored, type-safe implementation of the baseline
agent tool hook functions. It introduces clear structures for tool invocations,
results, and logs while maintaining exact behavioral compatibility with the
baseline implementation.

Key improvements:
- Clear dataclass-based structures for ToolResult and logging
- Centralized tool invocation logic to eliminate copy-paste
- Strategy pattern for configurable log message templates
- Backward-compatible conversion to baseline dict format
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


Tool = Callable[..., Any]


@dataclass
class ToolInvocation:
    """Represents a single tool invocation request."""
    tool: Tool
    name: str
    args: Dict[str, Any]


@dataclass
class ToolResult:
    """Structured result from a tool invocation.
    
    This encapsulates all information from a tool call, including metadata,
    execution status, and a list of log messages.
    """
    tool_name: str
    status: str  # "ok" or "error"
    error: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    output: Any = None
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to baseline-compatible dictionary format."""
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "error": self.error,
            "args": self.args,
            "output": self.output,
            "logs": self.logs,
        }


class LogStrategy:
    """Strategy for generating log messages during tool invocation."""
    
    def log_start(self, name: str, args: Dict[str, Any]) -> str:
        """Generate a log message for tool invocation start."""
        raise NotImplementedError
    
    def log_error(self, exc: Exception) -> str:
        """Generate a log message for an error."""
        raise NotImplementedError
    
    def log_end(self) -> str:
        """Generate a log message for successful completion."""
        raise NotImplementedError


class LogStrategyA(LogStrategy):
    """Log strategy matching call_tool_a baseline messages."""
    
    def log_start(self, name: str, args: Dict[str, Any]) -> str:
        return f"calling {name} with {args!r}"
    
    def log_error(self, exc: Exception) -> str:
        return f"error: {exc}"
    
    def log_end(self) -> str:
        return "done"


class LogStrategyB(LogStrategy):
    """Log strategy matching call_tool_b baseline messages."""
    
    def log_start(self, name: str, args: Dict[str, Any]) -> str:
        return f"tool {name} start {args!r}"
    
    def log_error(self, exc: Exception) -> str:
        return f"failed: {exc}"
    
    def log_end(self) -> str:
        return "ok"


class ToolCaller:
    """Centralized tool invocation handler.
    
    This class encapsulates the common logic for calling tools, handling
    exceptions, and collecting logs. It eliminates the copy-paste between
    the baseline call_tool_a and call_tool_b functions.
    """
    
    def __init__(self, log_strategy: LogStrategy):
        """Initialize with a log strategy."""
        self.log_strategy = log_strategy
    
    def call(self, tool: Tool, name: str, args: Dict[str, Any]) -> ToolResult:
        """Call a tool and return a structured result.
        
        Args:
            tool: The callable to invoke
            name: The name of the tool (for logging and result)
            args: Keyword arguments to pass to the tool
            
        Returns:
            ToolResult containing all invocation details
        """
        result = ToolResult(tool_name=name, status="ok", args=args)
        result.logs.append(self.log_strategy.log_start(name, args))
        
        try:
            output = tool(**args)
        except Exception as exc:
            result.status = "error"
            result.error = str(exc)
            result.logs.append(self.log_strategy.log_error(exc))
        else:
            result.output = output
            result.logs.append(self.log_strategy.log_end())
        
        return result


def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced wrapper around call_tool_a logic using the new architecture.
    
    This function maintains the exact interface and behavior of the baseline
    call_tool_a while delegating to the refactored ToolCaller.
    
    Args:
        tool: The callable to invoke
        name: The name of the tool
        args: Keyword arguments to pass to the tool
        
    Returns:
        Dictionary with tool_name, status, error, args, output, and logs
    """
    caller = ToolCaller(LogStrategyA())
    result = caller.call(tool, name, args)
    return result.to_dict()


def call_tool_b(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced wrapper around call_tool_b logic using the new architecture.
    
    This function maintains the exact interface and behavior of the baseline
    call_tool_b while delegating to the refactored ToolCaller.
    
    Args:
        tool: The callable to invoke
        name: The name of the tool
        args: Keyword arguments to pass to the tool
        
    Returns:
        Dictionary with tool_name, status, error, args, output, and logs
    """
    caller = ToolCaller(LogStrategyB())
    result = caller.call(tool, name, args)
    return result.to_dict()


class ToolOrchestrator:
    """Enhanced orchestrator for managing multiple tool invocations.
    
    This class replaces the baseline run_all function with a more flexible
    architecture that allows for different invocation strategies while
    maintaining backward compatibility.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.callers = {
            "a": ToolCaller(LogStrategyA()),
            "b": ToolCaller(LogStrategyB()),
        }
    
    def run_all_alternating(
        self, 
        tools: List[Tool], 
        names: List[str], 
        payloads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run tools in sequence, alternating between strategy A and B.
        
        This method implements the baseline run_all behavior using the
        enhanced architecture. It alternates between call strategies based
        on the index.
        
        Args:
            tools: List of callable tools
            names: List of tool names
            payloads: List of argument dictionaries
            
        Returns:
            List of result dictionaries in baseline format
        """
        results: List[Dict[str, Any]] = []
        for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
            caller = self.callers["a"] if index % 2 == 0 else self.callers["b"]
            result = caller.call(tool, name, args)
            results.append(result.to_dict())
        return results


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enhanced wrapper around baseline run_all using the new architecture.
    
    This function maintains the exact interface and behavior of the baseline
    run_all function while using the refactored ToolOrchestrator.
    
    Args:
        tools: List of callable tools
        names: List of tool names  
        payloads: List of argument dictionaries
        
    Returns:
        List of result dictionaries with same format as baseline
    """
    orchestrator = ToolOrchestrator()
    return orchestrator.run_all_alternating(tools, names, payloads)
