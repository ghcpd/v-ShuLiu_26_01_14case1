import unittest

from agent_tools_hook import call_tool_a, call_tool_b, run_all, ToolResult
import agent_tools_hook_origin as origin


def success_tool(a=1, b=2):
    return a + b


def failing_tool(*, reason="boom"):
    raise ValueError(reason)


class TestAgentToolsHook(unittest.TestCase):
    def test_call_tool_a_matches_baseline_success(self):
        args = {"a": 2, "b": 3}
        baseline = origin.call_tool_a(success_tool, "add", args)
        enhanced = call_tool_a(success_tool, "add", args)
        self.assertIsInstance(enhanced, ToolResult)
        self.assertEqual(baseline, enhanced.to_baseline_dict())

    def test_call_tool_b_matches_baseline_error(self):
        args = {"reason": "boom"}
        baseline = origin.call_tool_b(failing_tool, "exploder", args)
        enhanced = call_tool_b(failing_tool, "exploder", args)
        self.assertEqual(baseline, enhanced.to_baseline_dict())

    def test_run_all_matches_baseline_and_call_order(self):
        calls_seq_baseline = []

        def recorder_factory(seq_list, label):
            def tool(**kwargs):
                seq_list.append((label, dict(kwargs)))
                return f"done-{label}"

            return tool

        tools = [recorder_factory(calls_seq_baseline, "t1"), failing_tool, recorder_factory(calls_seq_baseline, "t3")]
        names = ["t1", "t2", "t3"]
        payloads = [{"x": 1}, {"reason": "boom"}, {"x": 9}]

        baseline_results = origin.run_all(tools, names, payloads)

        # Now run enhanced and record its own call sequence
        calls_seq_enhanced = []

        tools2 = [recorder_factory(calls_seq_enhanced, "t1"), failing_tool, recorder_factory(calls_seq_enhanced, "t3")]
        enhanced_results = run_all(tools2, names, payloads)

        # Compare baseline dicts to our converted dicts
        enhanced_dicts = [r.to_baseline_dict() for r in enhanced_results]
        self.assertEqual(baseline_results, enhanced_dicts)

        # Ensure the call sequences have the same labels and args in order
        self.assertEqual(calls_seq_baseline, calls_seq_enhanced)

    def test_roundtrip_from_and_to_baseline_dict(self):
        args = {"a": 5, "b": 7}
        enhanced = call_tool_a(success_tool, "adder", args)
        baseline = enhanced.to_baseline_dict()
        reconstructed = ToolResult.from_baseline_dict(baseline)
        self.assertEqual(reconstructed.to_baseline_dict(), baseline)


if __name__ == "__main__":
    unittest.main()
