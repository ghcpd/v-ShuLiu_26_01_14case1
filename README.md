# Agent Tool Hook — enhancement

What I changed
- Introduced a small, structured API around tool invocations (`ToolResult`, `LogRecord`, `Runner`).
- Centralized calling / exception / logging behavior so the two call variants no longer duplicate logic.
- Kept a fully compatible surface: `call_tool_a`, `call_tool_b`, and `run_all` return the exact dict shape and log strings the baseline produced.

Why
- The baseline (`agent_tools_hook_origin.py`) is correct but repetitive and fragile. The new design makes it easier to extend (structured logs, richer APIs) while preserving observable behavior for existing callers and tests.

Files added
- `agent_tools_hook.py` — enhanced implementation and structured API (`ToolResult`, `Runner`).
- `tests/test_agent_tools_hook.py` — compatibility and round-trip tests.
- `README.md` — this file.

Primary public API
- `call_tool_a(tool, name, args) -> dict` — backward-compatible (same output as baseline).
- `call_tool_b(tool, name, args) -> dict` — backward-compatible.
- `run_all(tools, names, payloads) -> list[dict]` — backward-compatible orchestrator.
- `ToolResult` / `LogRecord` — structured representations; use `ToolResult.to_baseline_dict()` to get the original dict shape.
- `Runner` — `run_all_structured(...)` and `call_structured(...)` for typed usage.

Quick example

```py
from agent_tools_hook import Runner, call_tool_a

# backward-compatible (returns baseline-shaped dict)
res = call_tool_a(lambda x: x*2, "double", {"x": 3})

# structured API
runner = Runner()
structured = runner.run_all_structured([lambda x: x+1], ["inc"], [{"x": 1}])
print(structured[0].to_baseline_dict())
```

Running tests (Windows)

From the repository root run:

    python run_tests.py

The script prefers `pytest` when available and falls back to `unittest` discovery. An exit code of `0` means all tests passed; any non-zero exit code indicates failure.
