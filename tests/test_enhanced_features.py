"""Tests for enhanced structured types and features.

This module tests the new structured types, conversions, and features
that go beyond the baseline implementation.
"""

import unittest
from typing import Any

from agent_hooks.core import ToolInvocation, ToolResult, invoke_tool
from agent_tools_hook import invoke_single_tool, run_all_tools


class TestStructuredTypes(unittest.TestCase):
    """Test structured types and their behavior."""
    
    def test_tool_invocation_creation(self):
        """Verify ToolInvocation can be created with proper fields."""
        def dummy_tool(x: int) -> int:
            return x
        
        invocation = ToolInvocation(
            tool=dummy_tool,
            name="dummy",
            args={"x": 42},
            log_style="a"
        )
        
        self.assertEqual(invocation.name, "dummy")
        self.assertEqual(invocation.args, {"x": 42})
        self.assertEqual(invocation.log_style, "a")
        self.assertIs(invocation.tool, dummy_tool)
    
    def test_tool_invocation_default_log_style(self):
        """Verify ToolInvocation defaults to log style 'a'."""
        def dummy_tool(x: int) -> int:
            return x
        
        invocation = ToolInvocation(tool=dummy_tool, name="test", args={})
        self.assertEqual(invocation.log_style, "a")
    
    def test_tool_invocation_invalid_log_style(self):
        """Verify ToolInvocation rejects invalid log styles."""
        def dummy_tool(x: int) -> int:
            return x
        
        with self.assertRaises(ValueError) as ctx:
            ToolInvocation(tool=dummy_tool, name="test", args={}, log_style="c")
        
        self.assertIn("log_style must be 'a' or 'b'", str(ctx.exception))
    
    def test_tool_result_to_dict(self):
        """Verify ToolResult.to_dict produces correct structure."""
        result = ToolResult(
            tool_name="test_tool",
            status="ok",
            error=None,
            args={"x": 1, "y": 2},
            output=3,
            logs=["log1", "log2"]
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["tool_name"], "test_tool")
        self.assertEqual(result_dict["status"], "ok")
        self.assertIsNone(result_dict["error"])
        self.assertEqual(result_dict["args"], {"x": 1, "y": 2})
        self.assertEqual(result_dict["output"], 3)
        self.assertEqual(result_dict["logs"], ["log1", "log2"])
    
    def test_tool_result_from_dict(self):
        """Verify ToolResult.from_dict reconstructs object correctly."""
        original_dict = {
            "tool_name": "test_tool",
            "status": "error",
            "error": "something went wrong",
            "args": {"a": 10},
            "output": None,
            "logs": ["started", "failed"]
        }
        
        result = ToolResult.from_dict(original_dict)
        
        self.assertEqual(result.tool_name, "test_tool")
        self.assertEqual(result.status, "error")
        self.assertEqual(result.error, "something went wrong")
        self.assertEqual(result.args, {"a": 10})
        self.assertIsNone(result.output)
        self.assertEqual(result.logs, ["started", "failed"])
    
    def test_tool_result_round_trip(self):
        """Verify ToolResult can round-trip through dict conversion."""
        original = ToolResult(
            tool_name="round_trip",
            status="ok",
            error=None,
            args={"val": 99},
            output="result",
            logs=["a", "b", "c"]
        )
        
        # Convert to dict and back
        as_dict = original.to_dict()
        reconstructed = ToolResult.from_dict(as_dict)
        
        # Should be equal
        self.assertEqual(original.tool_name, reconstructed.tool_name)
        self.assertEqual(original.status, reconstructed.status)
        self.assertEqual(original.error, reconstructed.error)
        self.assertEqual(original.args, reconstructed.args)
        self.assertEqual(original.output, reconstructed.output)
        self.assertEqual(original.logs, reconstructed.logs)


class TestEnhancedFeatures(unittest.TestCase):
    """Test enhanced features beyond baseline compatibility."""
    
    def test_invoke_tool_with_invocation_object(self):
        """Verify invoke_tool works with ToolInvocation objects."""
        def multiply(x: int, y: int) -> int:
            return x * y
        
        invocation = ToolInvocation(
            tool=multiply,
            name="multiply",
            args={"x": 6, "y": 7},
            log_style="a"
        )
        
        result = invoke_tool(invocation)
        
        self.assertIsInstance(result, ToolResult)
        self.assertEqual(result.tool_name, "multiply")
        self.assertEqual(result.status, "ok")
        self.assertIsNone(result.error)
        self.assertEqual(result.output, 42)
    
    def test_run_all_returns_structured_results(self):
        """Verify run_all_tools returns ToolResult objects."""
        def add(a: int, b: int) -> int:
            return a + b
        
        def sub(a: int, b: int) -> int:
            return a - b
        
        results = run_all_tools(
            tools=[add, sub],
            names=["add", "sub"],
            payloads=[{"a": 10, "b": 3}, {"a": 20, "b": 5}]
        )
        
        # All results should be ToolResult instances
        for result in results:
            self.assertIsInstance(result, ToolResult)
        
        # Check specific values
        self.assertEqual(results[0].output, 13)
        self.assertEqual(results[1].output, 15)
    
    def test_structured_error_handling(self):
        """Verify structured error information is preserved."""
        def failing_tool(x: int) -> int:
            raise TypeError("wrong type")
        
        result = invoke_single_tool(failing_tool, "fail", {"x": 1}, log_style="a")
        
        self.assertEqual(result.status, "error")
        self.assertEqual(result.error, "wrong type")
        self.assertIsNone(result.output)
        self.assertIn("error:", result.logs[1])
    
    def test_logs_are_mutable_list(self):
        """Verify logs field is a mutable list."""
        def simple_tool(x: int) -> int:
            return x
        
        result = invoke_single_tool(simple_tool, "simple", {"x": 5})
        
        # Should be able to append to logs
        original_len = len(result.logs)
        result.logs.append("custom log entry")
        
        self.assertEqual(len(result.logs), original_len + 1)
        self.assertEqual(result.logs[-1], "custom log entry")
    
    def test_tool_with_no_args(self):
        """Verify tools with no arguments work correctly."""
        def no_arg_tool() -> str:
            return "hello"
        
        result = invoke_single_tool(no_arg_tool, "greeter", {})
        
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.output, "hello")
        self.assertEqual(result.args, {})
    
    def test_tool_with_complex_output(self):
        """Verify tools can return complex data structures."""
        def complex_tool(x: int) -> dict:
            return {"result": x * 2, "metadata": {"type": "doubled"}}
        
        result = invoke_single_tool(complex_tool, "complex", {"x": 21})
        
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.output["result"], 42)
        self.assertEqual(result.output["metadata"]["type"], "doubled")
    
    def test_multiple_sequential_invocations(self):
        """Verify multiple sequential invocations maintain independence."""
        def counter(value: int) -> int:
            return value + 1
        
        result1 = invoke_single_tool(counter, "counter", {"value": 0})
        result2 = invoke_single_tool(counter, "counter", {"value": 5})
        result3 = invoke_single_tool(counter, "counter", {"value": 10})
        
        # Results should be independent
        self.assertEqual(result1.output, 1)
        self.assertEqual(result2.output, 6)
        self.assertEqual(result3.output, 11)
        
        # Each should have its own log list
        self.assertIsNot(result1.logs, result2.logs)
        self.assertIsNot(result2.logs, result3.logs)


if __name__ == "__main__":
    unittest.main()
