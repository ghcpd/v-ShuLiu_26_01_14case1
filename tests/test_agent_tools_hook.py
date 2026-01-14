import unittest

import agent_tools_hook_origin as origin
import agent_tools_hook as enhanced


class DummyCalls:
    def __init__(self):
        self.calls = []

    def make_return(self, value):
        def _fn(**kwargs):
            self.calls.append(("return", kwargs))
            return value

        return _fn

    def make_error(self, msg):
        def _fn(**kwargs):
            self.calls.append(("error", kwargs))
            raise ValueError(msg)

        return _fn


class TestCompatibility(unittest.TestCase):
    def test_call_tool_a_success_matches_origin(self):
        tool = lambda x: x + 1
        args = {"x": 1}

        a = origin.call_tool_a(tool, "add1", args)
        b = enhanced.call_tool_a(tool, "add1", args)

        self.assertEqual(a, b)

    def test_call_tool_b_error_matches_origin(self):
        def boom(**kwargs):
            raise RuntimeError("boom!")

        args = {"n": 5}
        a = origin.call_tool_b(boom, "boomtool", args)
        b = enhanced.call_tool_b(boom, "boomtool", args)

        self.assertEqual(a, b)
        # ensure logs preserved order and messages
        self.assertEqual(a["logs"][0], b["logs"][0])
        self.assertEqual(a["logs"][-1], b["logs"][-1])

    def test_run_all_preserves_order_and_alternation(self):
        d = DummyCalls()
        tools = [d.make_return(1), d.make_error("nope"), d.make_return(3)]
        names = ["t1", "t2", "t3"]
        payloads = [{"a": 1}, {"b": 2}, {"c": 3}]

        orig = origin.run_all(tools, names, payloads)
        enh = enhanced.run_all(tools, names, payloads)

        self.assertEqual(orig, enh)
        # ensure the underlying call order (side effects) is identical
        self.assertEqual(d.calls[0][1], {"a": 1})
        self.assertEqual(d.calls[1][1], {"b": 2})
        self.assertEqual(d.calls[2][1], {"c": 3})

    def test_structured_roundtrip_and_helpers(self):
        def greet(**kwargs):
            return f"hi {kwargs['who']}"

        args = {"who": "you"}
        tr = enhanced.Runner().call_structured(greet, "greet", args, variant="a")
        baseline = origin.call_tool_a(greet, "greet", args)

        # structured -> baseline dict matches origin
        self.assertEqual(tr.to_baseline_dict(), baseline)

        # baseline -> structured -> baseline is stable
        tr2 = enhanced.ToolResult.from_baseline_dict(baseline)
        self.assertEqual(tr2.to_baseline_dict(), baseline)

    def test_no_special_casing_on_names_or_tools(self):
        # ensure generic behavior: arbitrary callables and names are supported
        class C:
            def __call__(self, **k):
                return k

        obj = C()
        args = {"x": 42}
        a = origin.call_tool_a(obj, "custom", args)
        b = enhanced.call_tool_a(obj, "custom", args)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
