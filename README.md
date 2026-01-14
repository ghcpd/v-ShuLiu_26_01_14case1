# Agent Tool Hook — Enhanced implementation

This repository contains a tiny baseline implementation (`agent_tools_hook_origin.py`) and
an enhanced, structured wrapper implemented in `agent_tools_hook.py`.

Key improvements
- Introduces `ToolResult` (a dataclass) to represent tool invocation results.
- Centralized calling logic (`_call_tool`) removes duplication between variants.
- `ToolResult.to_dict()` preserves exact baseline dictionary shape and log messages
  so observable behavior remains compatible.

Files added
- `agent_tools_hook.py` — enhanced API and types (`ToolResult`, `call_tool_a`, `call_tool_b`, `run_all`).
- `tests/test_enhanced_hook.py` — automated tests that compare the enhanced API with the baseline.

Public API (short example)

- call_tool_a(tool, name, args) -> ToolResult
- call_tool_b(tool, name, args) -> ToolResult
- run_all(tools, names, payloads) -> List[ToolResult]
- ToolResult.to_dict() -> dict  # converts back to baseline-compatible dict

Example

    from agent_tools_hook import call_tool_a

    def greet(who):
        return f"hello {who}"

    res = call_tool_a(greet, "greet", {"who": "world"})
    print(res.to_dict())

Running tests

Run the test suite from the repository root on Windows with:

    python run_tests.py

Exit codes
- 0: all tests passed
- non-zero: one or more tests failed
