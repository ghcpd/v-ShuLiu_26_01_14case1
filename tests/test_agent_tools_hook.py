import unittest
from typing import Any, Dict

from agent_tools_hook_origin import call_tool_a, call_tool_b, run_all as run_all_baseline
from agent_tools_hook import call_tool, run_all, ToolResult


class TestAgentToolsHook(unittest.TestCase):
    def test_call_tool_a_equivalence(self):
        def dummy_tool(x: int) -> int:
            return x * 2

        name = "test_tool"
        args = {"x": 5}

        baseline_result = call_tool_a(dummy_tool, name, args)
        enhanced_result = call_tool('a', dummy_tool, name, args).to_dict()

        self.assertEqual(baseline_result, enhanced_result)

    def test_call_tool_b_equivalence(self):
        def dummy_tool(x: int) -> int:
            return x * 2

        name = "test_tool"
        args = {"x": 5}

        baseline_result = call_tool_b(dummy_tool, name, args)
        enhanced_result = call_tool('b', dummy_tool, name, args).to_dict()

        self.assertEqual(baseline_result, enhanced_result)

    def test_call_tool_a_error(self):
        def failing_tool():
            raise ValueError("test error")

        name = "failing_tool"
        args = {}

        baseline_result = call_tool_a(failing_tool, name, args)
        enhanced_result = call_tool('a', failing_tool, name, args).to_dict()

        self.assertEqual(baseline_result, enhanced_result)

    def test_call_tool_b_error(self):
        def failing_tool():
            raise ValueError("test error")

        name = "failing_tool"
        args = {}

        baseline_result = call_tool_b(failing_tool, name, args)
        enhanced_result = call_tool('b', failing_tool, name, args).to_dict()

        self.assertEqual(baseline_result, enhanced_result)

    def test_run_all_equivalence(self):
        def tool1(x: int) -> int:
            return x + 1

        def tool2(y: str) -> str:
            return y.upper()

        def tool3(z: float) -> float:
            return z * 2

        tools = [tool1, tool2, tool3]
        names = ["add_one", "upper", "double"]
        payloads = [{"x": 10}, {"y": "hello"}, {"z": 3.5}]

        baseline_results = run_all_baseline(tools, names, payloads)
        enhanced_results = run_all(tools, names, payloads)

        self.assertEqual(baseline_results, enhanced_results)

    def test_tool_result_to_dict(self):
        result = ToolResult(
            tool_name="test",
            status="ok",
            error=None,
            args={"a": 1},
            output=42,
            logs=["log1", "log2"]
        )
        expected = {
            "tool_name": "test",
            "status": "ok",
            "error": None,
            "args": {"a": 1},
            "output": 42,
            "logs": ["log1", "log2"]
        }
        self.assertEqual(result.to_dict(), expected)


if __name__ == "__main__":
    unittest.main()