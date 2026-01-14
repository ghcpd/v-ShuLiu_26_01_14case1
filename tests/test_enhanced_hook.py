import builtins
import pytest

import agent_tools_hook_origin as origin
import agent_tools_hook as enhanced


def test_call_tool_a_success_and_error_match_baseline():
    # success tool
    def succeed(x):
        return x * 2

    # error tool
    def fail(x):
        raise ValueError(f"bad {x}")

    # call baseline and enhanced for success
    base_ok = origin.call_tool_a(succeed, "succeed", {"x": 3})
    enh_ok = enhanced.call_tool_a(succeed, "succeed", {"x": 3}).to_dict()
    assert enh_ok == base_ok

    # call baseline and enhanced for error
    base_err = origin.call_tool_a(fail, "fail", {"x": 5})
    enh_err = enhanced.call_tool_a(fail, "fail", {"x": 5}).to_dict()
    assert enh_err == base_err


def test_call_tool_b_success_and_error_match_baseline():
    def succeed(a, b=1):
        return a + b

    def fail(a, b=1):
        raise RuntimeError("boom")

    base_ok = origin.call_tool_b(succeed, "sum", {"a": 2, "b": 3})
    enh_ok = enhanced.call_tool_b(succeed, "sum", {"a": 2, "b": 3}).to_dict()
    assert enh_ok == base_ok

    base_err = origin.call_tool_b(fail, "sum", {"a": 2, "b": 3})
    enh_err = enhanced.call_tool_b(fail, "sum", {"a": 2, "b": 3}).to_dict()
    assert enh_err == base_err


def test_run_all_preserves_call_order_and_outputs():
    calls = []

    def make_tool(i):
        def tool(x):
            calls.append((i, x))
            return f"t{i}:{x}"

        return tool

    tools = [make_tool(i) for i in range(6)]
    names = [f"tool{i}" for i in range(6)]
    payloads = [{"x": i} for i in range(6)]

    base_results = origin.run_all(tools, names, payloads)

    # reset and capture calls for enhanced run
    calls.clear()
    enh_results = enhanced.run_all(tools, names, payloads)

    # ensure the underlying tools were called the same number of times and in the same order
    assert len(calls) == 6
    assert calls == [(i, i) for i in range(6)]

    # compare baseline dicts with enhanced -> to_dict()
    enh_dicts = [r.to_dict() for r in enh_results]
    assert enh_dicts == base_results


def test_structured_result_can_hold_meta_but_exports_original_logs():
    def echo(msg):
        return msg

    res = enhanced.call_tool_a(echo, "echo", {"msg": "hi"})
    # attach some structured metadata (allowed by constraint 3)
    res.meta["duration_ms"] = 12

    baseline = origin.call_tool_a(echo, "echo", {"msg": "hi"})
    assert res.to_dict() == baseline
    # ensure the structured metadata does not appear in baseline dict
    assert "duration_ms" not in res.to_dict()
