# Agent Tool Hook Enhancement

This small enhancement introduces a structured, testable wrapper around the
baseline, repetitive agent tool hook layer found in
`agent_tools_hook_origin.py`.

## What I changed (new files)

- `agent_tools_hook.py` ✅
  - Introduces a `ToolResult` dataclass and centralized invocation logic.
  - Exposes `call_tool_a`, `call_tool_b`, and `run_all` that return structured
    `ToolResult` objects. Use `ToolResult.to_baseline_dict()` to obtain a plain
    dictionary compatible with the baseline shape.

- `tests/test_agent_tools_hook.py` ✅
  - Tests that compare the new structured API with the baseline functions,
    ensuring core fields and log messages are preserved exactly and that
    call order and error handling are unchanged.

## Design highlights

- Centralized `_invoke` implements the shared logic for calling tools,
  handling exceptions, and producing the exact log messages used by the
  baseline functions. This eliminates the copy-paste baseline pain point while
  allowing richer, typed results via `ToolResult`.

- Conversion helpers (`ToolResult.to_baseline_dict()` and
  `ToolResult.from_baseline_dict()`) make it straightforward to interoperate
  with the baseline's loose dict-based format without losing or changing
  semantics.

## How to run tests

From the repository root (Windows 10+, Python 3.8+):

    python run_tests.py

`run_tests.py` will try `pytest` first and fall back to `unittest` discovery if
`pytest` is not available. The process exit code is 0 on success and non-zero
on any failure (no custom PASS messages are printed).
