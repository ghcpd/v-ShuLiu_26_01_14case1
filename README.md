# Agent Tool Hook Enhancement

## Overview

This project enhances the baseline agent tool hook implementation with a clearer, more modular design while maintaining exact behavioral compatibility. The baseline implementation is small but contains significant code duplication and loose typing that makes it difficult to extend.

## Baseline Pain Points

The original implementation in `agent_tools_hook_origin.py` exhibits several design issues:

1. **Heavy Copy-Paste**: The `call_tool_a` and `call_tool_b` functions are nearly identical, differing only in log message templates. This duplication makes maintenance error-prone.

2. **Unstructured Results**: Results are returned as plain dictionaries without type hints or formal structure, making it unclear what fields are guaranteed to exist.

3. **Mixed Concerns**: Tool invocation logic, error handling, logging, and orchestration are all interleaved in single functions.

4. **Inflexible Logging**: Log messages are hardcoded into each function, making it impossible to customize logging behavior without modifying function code.

5. **No Reusable Components**: Each function implements its own try-catch and result building, preventing code reuse.

## Enhanced Architecture

The enhanced implementation (`agent_tools_hook.py`) introduces a modular design with clear separation of concerns:

### Core Types and Structures

#### `ToolInvocation`
A dataclass representing a single tool invocation request with:
- `tool`: The callable to invoke
- `name`: Tool identifier for logging and results
- `args`: Keyword arguments to pass to the tool

#### `ToolResult`
A structured dataclass encapsulating all information from a tool call:
- `tool_name`: Identifier of the invoked tool
- `status`: Either "ok" or "error"
- `error`: Optional error message if status is "error"
- `args`: The arguments that were passed
- `output`: The return value (None if error)
- `logs`: List of log messages from invocation

The `to_dict()` method provides backward compatibility by converting to the baseline dictionary format.

### Strategy Pattern for Logging

Two strategy classes encapsulate the different logging behaviors:

#### `LogStrategyA`
Produces log messages matching `call_tool_a` format:
- Start: `"calling {name} with {args!r}"`
- Error: `"error: {exception}"`
- Success: `"done"`

#### `LogStrategyB`
Produces log messages matching `call_tool_b` format:
- Start: `"tool {name} start {args!r}"`
- Error: `"failed: {exception}"`
- Success: `"ok"`

### Central Tool Invocation Logic

#### `ToolCaller`
Encapsulates the common logic for calling tools, handling exceptions, and collecting logs:

```python
caller = ToolCaller(LogStrategyA())
result = caller.call(my_tool, "tool_name", {"arg": value})
```

This eliminates the copy-paste by centralizing:
- Tool invocation with exception handling
- Log message generation via strategy pattern
- Result object construction
- Status and error field management

### Orchestration

#### `ToolOrchestrator`
Manages multiple tool invocations with configurable strategies:

```python
orchestrator = ToolOrchestrator()
results = orchestrator.run_all_alternating(tools, names, payloads)
```

The `run_all_alternating` method replicates the baseline `run_all` behavior by alternating between strategies based on invocation index.

### Backward-Compatible Functions

The public functions `call_tool_a`, `call_tool_b`, and `run_all` are reimplemented as thin wrappers around the enhanced components, ensuring exact API and behavioral compatibility:

```python
def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    caller = ToolCaller(LogStrategyA())
    result = caller.call(tool, name, args)
    return result.to_dict()
```

## Design Benefits

1. **No Code Duplication**: Common logic is centralized in `ToolCaller`.
2. **Clear Typing**: All structures are typed dataclasses, enabling IDE support and static analysis.
3. **Extensibility**: New log strategies can be added by subclassing `LogStrategy` without modifying existing code.
4. **Testability**: Each component can be tested independently.
5. **Backward Compatibility**: Existing code using the baseline functions continues to work unchanged.
6. **Maintainability**: Concerns are well-separated, making the code easier to understand and modify.

## Running Tests

All tests are located in the `tests/` directory and are automatically discovered by the test runner.

### Using Python's unittest (fallback)

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Using pytest (preferred)

```bash
pytest tests/ -v
```

### Using the unified test entry point

```bash
python run_tests.py
```

The test runner will:
1. Try to use `pytest` if available
2. Fall back to `unittest` if `pytest` is not installed
3. Exit with code 0 if all tests pass
4. Exit with non-zero code if any test fails

## Test Coverage

The test suite (`tests/test_agent_tools_hook.py`) includes:

- **Basic Behavior Tests**: Verify that enhanced functions produce identical results to baseline
- **Log Message Tests**: Ensure log sequences match exactly between implementations
- **Orchestration Tests**: Test that `run_all` correctly alternates between strategies
- **Error Handling Tests**: Verify exception handling and error classification
- **Type Structure Tests**: Validate `ToolResult` and dataclass conversions
- **Strategy Tests**: Verify each log strategy produces correct messages
- **Compatibility Tests**: Comprehensive verification of backward compatibility

Each test compares baseline results with enhanced results to ensure absolute compatibility.

## File Structure

```
agent_tools_hook_origin.py    # Read-only baseline implementation
agent_tools_hook.py           # Enhanced implementation with clear architecture
tests/
  test_agent_tools_hook.py    # Comprehensive test suite
run_tests.py                  # Unified test entry point (read-only)
README.md                     # This file
```

## System Requirements

- Python 3.8+ (tested on Windows 10+)
- Standard library only (no external dependencies required)
- Optional: `pytest` for enhanced test output (falls back to `unittest`)

## Example Usage

### Using the enhanced API directly

```python
from agent_tools_hook import ToolCaller, LogStrategyA, ToolOrchestrator

# Single tool invocation with strategy A
caller = ToolCaller(LogStrategyA())
result = caller.call(my_tool, "my_tool", {"x": 5})

# Multiple tools with alternating strategies
orchestrator = ToolOrchestrator()
results = orchestrator.run_all_alternating(tools, names, payloads)
```

### Backward compatibility with baseline interface

```python
from agent_tools_hook import call_tool_a, call_tool_b, run_all

# These functions maintain the exact baseline interface
result = call_tool_a(my_tool, "name", {"arg": value})
result = call_tool_b(my_tool, "name", {"arg": value})
results = run_all(tools, names, payloads)
```

## Implementation Notes

- All types are properly annotated for Python 3.8+ compatibility
- The implementation uses only the Python standard library
- Error messages from exceptions are preserved exactly
- Log messages match the baseline format precisely
- The architecture is designed for future extensions (e.g., additional strategies, metrics collection)
