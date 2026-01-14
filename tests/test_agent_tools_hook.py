"""Tests for the enhanced agent tool hook implementation.

These tests verify that:
1. The enhanced API produces identical results to the baseline
2. Core fields (tool_name, status, error, args, output, logs) are preserved
3. The log message sequences match exactly
4. ToolResult can be converted back to baseline dict format
5. Error handling and classification works correctly
"""

import unittest
from typing import Any, Dict
import agent_tools_hook_origin as baseline
import agent_tools_hook as enhanced


class TestToolCallersBasicBehavior(unittest.TestCase):
    """Test that enhanced call_tool_a and call_tool_b produce baseline-compatible results."""
    
    def test_call_tool_a_success(self):
        """Test call_tool_a with a successful tool invocation."""
        def dummy_tool(x: int, y: int) -> int:
            return x + y
        
        baseline_result = baseline.call_tool_a(dummy_tool, "add", {"x": 2, "y": 3})
        enhanced_result = enhanced.call_tool_a(dummy_tool, "add", {"x": 2, "y": 3})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["status"], "ok")
        self.assertEqual(enhanced_result["output"], 5)
        self.assertIsNone(enhanced_result["error"])
    
    def test_call_tool_b_success(self):
        """Test call_tool_b with a successful tool invocation."""
        def dummy_tool(x: int, y: int) -> int:
            return x * y
        
        baseline_result = baseline.call_tool_b(dummy_tool, "multiply", {"x": 4, "y": 5})
        enhanced_result = enhanced.call_tool_b(dummy_tool, "multiply", {"x": 4, "y": 5})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["status"], "ok")
        self.assertEqual(enhanced_result["output"], 20)
    
    def test_call_tool_a_with_error(self):
        """Test call_tool_a error handling."""
        def failing_tool() -> None:
            raise ValueError("Something went wrong")
        
        baseline_result = baseline.call_tool_a(failing_tool, "bad_tool", {})
        enhanced_result = enhanced.call_tool_a(failing_tool, "bad_tool", {})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["status"], "error")
        self.assertEqual(enhanced_result["error"], "Something went wrong")
        self.assertIsNone(enhanced_result["output"])
    
    def test_call_tool_b_with_error(self):
        """Test call_tool_b error handling."""
        def failing_tool() -> None:
            raise RuntimeError("Tool failed")
        
        baseline_result = baseline.call_tool_b(failing_tool, "bad_tool", {})
        enhanced_result = enhanced.call_tool_b(failing_tool, "bad_tool", {})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["status"], "error")
        self.assertEqual(enhanced_result["error"], "Tool failed")


class TestLogMessages(unittest.TestCase):
    """Test that log message sequences match exactly between baseline and enhanced."""
    
    def test_call_tool_a_log_messages(self):
        """Test that call_tool_a produces correct log messages."""
        def dummy_tool(x: int) -> int:
            return x * 2
        
        baseline_result = baseline.call_tool_a(dummy_tool, "double", {"x": 5})
        enhanced_result = enhanced.call_tool_a(dummy_tool, "double", {"x": 5})
        
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
        self.assertEqual(len(enhanced_result["logs"]), 2)
        self.assertIn("calling double with", enhanced_result["logs"][0])
        self.assertEqual(enhanced_result["logs"][1], "done")
    
    def test_call_tool_b_log_messages(self):
        """Test that call_tool_b produces correct log messages."""
        def dummy_tool(x: int) -> int:
            return x * 3
        
        baseline_result = baseline.call_tool_b(dummy_tool, "triple", {"x": 4})
        enhanced_result = enhanced.call_tool_b(dummy_tool, "triple", {"x": 4})
        
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
        self.assertEqual(len(enhanced_result["logs"]), 2)
        self.assertIn("tool triple start", enhanced_result["logs"][0])
        self.assertEqual(enhanced_result["logs"][1], "ok")
    
    def test_call_tool_a_error_logs(self):
        """Test call_tool_a error log messages."""
        def failing_tool() -> None:
            raise ValueError("Bad input")
        
        baseline_result = baseline.call_tool_a(failing_tool, "fail", {})
        enhanced_result = enhanced.call_tool_a(failing_tool, "fail", {})
        
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
        self.assertIn("error:", enhanced_result["logs"][1])
    
    def test_call_tool_b_error_logs(self):
        """Test call_tool_b error log messages."""
        def failing_tool() -> None:
            raise RuntimeError("Execution failed")
        
        baseline_result = baseline.call_tool_b(failing_tool, "fail", {})
        enhanced_result = enhanced.call_tool_b(failing_tool, "fail", {})
        
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
        self.assertIn("failed:", enhanced_result["logs"][1])


class TestRunAllOrchestration(unittest.TestCase):
    """Test the orchestrator run_all function."""
    
    def test_run_all_alternating(self):
        """Test that run_all correctly alternates between strategy A and B."""
        def tool_a() -> str:
            return "result_a"
        
        def tool_b() -> str:
            return "result_b"
        
        def tool_c() -> str:
            return "result_c"
        
        tools = [tool_a, tool_b, tool_c]
        names = ["tool1", "tool2", "tool3"]
        payloads = [{}, {}, {}]
        
        baseline_results = baseline.run_all(tools, names, payloads)
        enhanced_results = enhanced.run_all(tools, names, payloads)
        
        self.assertEqual(len(baseline_results), 3)
        self.assertEqual(len(enhanced_results), 3)
        
        # First should use strategy A
        self.assertIn("calling", baseline_results[0]["logs"][0])
        self.assertEqual(baseline_results[0], enhanced_results[0])
        
        # Second should use strategy B
        self.assertIn("tool tool2 start", baseline_results[1]["logs"][0])
        self.assertEqual(baseline_results[1], enhanced_results[1])
        
        # Third should use strategy A
        self.assertIn("calling", baseline_results[2]["logs"][0])
        self.assertEqual(baseline_results[2], enhanced_results[2])
    
    def test_run_all_with_errors(self):
        """Test run_all with mixed success and error cases."""
        def good_tool(x: int) -> int:
            return x * 2
        
        def bad_tool() -> None:
            raise ValueError("Tool failed")
        
        tools = [good_tool, bad_tool, good_tool]
        names = ["calc1", "error_tool", "calc2"]
        payloads = [{"x": 5}, {}, {"x": 3}]
        
        baseline_results = baseline.run_all(tools, names, payloads)
        enhanced_results = enhanced.run_all(tools, names, payloads)
        
        self.assertEqual(len(baseline_results), 3)
        self.assertEqual(baseline_results, enhanced_results)
        
        self.assertEqual(enhanced_results[0]["status"], "ok")
        self.assertEqual(enhanced_results[0]["output"], 10)
        
        self.assertEqual(enhanced_results[1]["status"], "error")
        self.assertIsNotNone(enhanced_results[1]["error"])
        
        self.assertEqual(enhanced_results[2]["status"], "ok")
        self.assertEqual(enhanced_results[2]["output"], 6)


class TestToolResultStructure(unittest.TestCase):
    """Test the ToolResult dataclass and its conversion to dict."""
    
    def test_tool_result_to_dict_success(self):
        """Test ToolResult conversion to dict for successful invocation."""
        result = enhanced.ToolResult(
            tool_name="test_tool",
            status="ok",
            args={"x": 1},
            output="success",
            logs=["log1", "log2"]
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["tool_name"], "test_tool")
        self.assertEqual(result_dict["status"], "ok")
        self.assertIsNone(result_dict["error"])
        self.assertEqual(result_dict["args"], {"x": 1})
        self.assertEqual(result_dict["output"], "success")
        self.assertEqual(result_dict["logs"], ["log1", "log2"])
    
    def test_tool_result_to_dict_error(self):
        """Test ToolResult conversion to dict for error case."""
        result = enhanced.ToolResult(
            tool_name="bad_tool",
            status="error",
            error="Something failed",
            args={"y": 2},
            logs=["log1", "error log"]
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict["tool_name"], "bad_tool")
        self.assertEqual(result_dict["status"], "error")
        self.assertEqual(result_dict["error"], "Something failed")
        self.assertIsNone(result_dict["output"])


class TestLogStrategies(unittest.TestCase):
    """Test log strategy implementations."""
    
    def test_log_strategy_a(self):
        """Test LogStrategyA produces correct messages."""
        strategy = enhanced.LogStrategyA()
        
        start_msg = strategy.log_start("my_tool", {"a": 1, "b": 2})
        error_msg = strategy.log_error(ValueError("test error"))
        end_msg = strategy.log_end()
        
        self.assertIn("calling my_tool with", start_msg)
        self.assertIn("error:", error_msg)
        self.assertEqual(end_msg, "done")
    
    def test_log_strategy_b(self):
        """Test LogStrategyB produces correct messages."""
        strategy = enhanced.LogStrategyB()
        
        start_msg = strategy.log_start("my_tool", {"a": 1, "b": 2})
        error_msg = strategy.log_error(RuntimeError("test error"))
        end_msg = strategy.log_end()
        
        self.assertIn("tool my_tool start", start_msg)
        self.assertIn("failed:", error_msg)
        self.assertEqual(end_msg, "ok")


class TestToolCaller(unittest.TestCase):
    """Test the ToolCaller class."""
    
    def test_tool_caller_with_strategy_a(self):
        """Test ToolCaller with LogStrategyA."""
        caller = enhanced.ToolCaller(enhanced.LogStrategyA())
        
        def dummy_tool(x: int) -> int:
            return x + 1
        
        result = caller.call(dummy_tool, "increment", {"x": 5})
        
        self.assertEqual(result.tool_name, "increment")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.output, 6)
        self.assertIsNone(result.error)
        self.assertEqual(len(result.logs), 2)
        self.assertIn("calling", result.logs[0])
    
    def test_tool_caller_with_strategy_b(self):
        """Test ToolCaller with LogStrategyB."""
        caller = enhanced.ToolCaller(enhanced.LogStrategyB())
        
        def dummy_tool(x: int) -> int:
            return x * 2
        
        result = caller.call(dummy_tool, "double", {"x": 3})
        
        self.assertEqual(result.tool_name, "double")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.output, 6)
        self.assertEqual(len(result.logs), 2)
        self.assertIn("tool", result.logs[0])
    
    def test_tool_caller_error_handling(self):
        """Test ToolCaller error handling."""
        caller = enhanced.ToolCaller(enhanced.LogStrategyA())
        
        def failing_tool() -> None:
            raise RuntimeError("Tool crashed")
        
        result = caller.call(failing_tool, "crash_tool", {})
        
        self.assertEqual(result.status, "error")
        self.assertEqual(result.error, "Tool crashed")
        self.assertIsNone(result.output)
        self.assertEqual(len(result.logs), 2)
        self.assertIn("error:", result.logs[1])


class TestToolOrchestrator(unittest.TestCase):
    """Test the ToolOrchestrator class."""
    
    def test_orchestrator_run_all_alternating(self):
        """Test ToolOrchestrator.run_all_alternating method."""
        orchestrator = enhanced.ToolOrchestrator()
        
        def tool_one() -> str:
            return "one"
        
        def tool_two() -> str:
            return "two"
        
        tools = [tool_one, tool_two]
        names = ["first", "second"]
        payloads = [{}, {}]
        
        results = orchestrator.run_all_alternating(tools, names, payloads)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "ok")
        self.assertEqual(results[1]["status"], "ok")
        # First uses strategy A (calling)
        self.assertIn("calling", results[0]["logs"][0])
        # Second uses strategy B (tool)
        self.assertIn("tool", results[1]["logs"][0])


class TestCompatibilityWithBaseline(unittest.TestCase):
    """Comprehensive tests ensuring backward compatibility with baseline."""
    
    def test_results_structure_matches_baseline(self):
        """Test that result structure matches baseline exactly."""
        def sample_tool(value: str) -> str:
            return f"processed: {value}"
        
        baseline_result = baseline.call_tool_a(sample_tool, "processor", {"value": "test"})
        enhanced_result = enhanced.call_tool_a(sample_tool, "processor", {"value": "test"})
        
        # Check all fields are present
        expected_keys = {"tool_name", "status", "error", "args", "output", "logs"}
        self.assertEqual(set(baseline_result.keys()), expected_keys)
        self.assertEqual(set(enhanced_result.keys()), expected_keys)
        
        # Check types and values
        self.assertEqual(baseline_result, enhanced_result)
    
    def test_empty_args_handling(self):
        """Test handling of tools with no arguments."""
        def no_arg_tool() -> str:
            return "result"
        
        baseline_result = baseline.call_tool_a(no_arg_tool, "noargs", {})
        enhanced_result = enhanced.call_tool_a(no_arg_tool, "noargs", {})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["args"], {})
    
    def test_complex_args_preservation(self):
        """Test preservation of complex argument types."""
        def complex_tool(data: Dict[str, Any], items: list) -> Dict[str, Any]:
            return {"processed": True, "count": len(items)}
        
        args = {"data": {"nested": "value"}, "items": [1, 2, 3]}
        
        baseline_result = baseline.call_tool_b(complex_tool, "complex", args)
        enhanced_result = enhanced.call_tool_b(complex_tool, "complex", args)
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["args"], args)
        self.assertEqual(enhanced_result["output"]["count"], 3)
    
    def test_exception_message_preservation(self):
        """Test that exception messages are preserved exactly."""
        def tool_with_custom_error() -> None:
            raise ValueError("Custom error message with special chars: !@#$")
        
        baseline_result = baseline.call_tool_b(tool_with_custom_error, "error_tool", {})
        enhanced_result = enhanced.call_tool_b(tool_with_custom_error, "error_tool", {})
        
        self.assertEqual(baseline_result, enhanced_result)
        self.assertEqual(enhanced_result["error"], "Custom error message with special chars: !@#$")


if __name__ == "__main__":
    unittest.main()
