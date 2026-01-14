"""Tests comparing enhanced implementation against baseline behavior.

This module verifies that the enhanced agent_tools_hook implementation
maintains full compatibility with the baseline agent_tools_hook_origin
functions while providing better structure.
"""

import unittest
from typing import Any, Dict, List

from agent_tools_hook_origin import call_tool_a, call_tool_b, run_all
from agent_tools_hook import ToolResult, run_all_tools


class TestBaselineCompatibility(unittest.TestCase):
    """Test that enhanced implementation matches baseline behavior."""
    
    def test_single_tool_success_style_a(self):
        """Verify single tool invocation with style 'a' matches baseline."""
        def sample_tool(x: int, y: int) -> int:
            return x + y
        
        # Run baseline
        baseline_result = call_tool_a(sample_tool, "add", {"x": 3, "y": 5})
        
        # Run enhanced (manually using style 'a')
        from agent_tools_hook import invoke_single_tool
        enhanced_result_obj = invoke_single_tool(sample_tool, "add", {"x": 3, "y": 5}, log_style="a")
        enhanced_result = enhanced_result_obj.to_dict()
        
        # Compare all fields
        self.assertEqual(baseline_result["tool_name"], enhanced_result["tool_name"])
        self.assertEqual(baseline_result["status"], enhanced_result["status"])
        self.assertEqual(baseline_result["error"], enhanced_result["error"])
        self.assertEqual(baseline_result["args"], enhanced_result["args"])
        self.assertEqual(baseline_result["output"], enhanced_result["output"])
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
    
    def test_single_tool_success_style_b(self):
        """Verify single tool invocation with style 'b' matches baseline."""
        def sample_tool(x: int, y: int) -> int:
            return x * y
        
        # Run baseline
        baseline_result = call_tool_b(sample_tool, "multiply", {"x": 4, "y": 7})
        
        # Run enhanced (manually using style 'b')
        from agent_tools_hook import invoke_single_tool
        enhanced_result_obj = invoke_single_tool(sample_tool, "multiply", {"x": 4, "y": 7}, log_style="b")
        enhanced_result = enhanced_result_obj.to_dict()
        
        # Compare all fields
        self.assertEqual(baseline_result["tool_name"], enhanced_result["tool_name"])
        self.assertEqual(baseline_result["status"], enhanced_result["status"])
        self.assertEqual(baseline_result["error"], enhanced_result["error"])
        self.assertEqual(baseline_result["args"], enhanced_result["args"])
        self.assertEqual(baseline_result["output"], enhanced_result["output"])
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
    
    def test_single_tool_error_style_a(self):
        """Verify error handling with style 'a' matches baseline."""
        def failing_tool(x: int) -> int:
            raise ValueError("test error")
        
        # Run baseline
        baseline_result = call_tool_a(failing_tool, "fail", {"x": 1})
        
        # Run enhanced
        from agent_tools_hook import invoke_single_tool
        enhanced_result_obj = invoke_single_tool(failing_tool, "fail", {"x": 1}, log_style="a")
        enhanced_result = enhanced_result_obj.to_dict()
        
        # Compare all fields
        self.assertEqual(baseline_result["tool_name"], enhanced_result["tool_name"])
        self.assertEqual(baseline_result["status"], "error")
        self.assertEqual(enhanced_result["status"], "error")
        self.assertEqual(baseline_result["error"], enhanced_result["error"])
        self.assertEqual(baseline_result["args"], enhanced_result["args"])
        self.assertIsNone(baseline_result["output"])
        self.assertIsNone(enhanced_result["output"])
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
    
    def test_single_tool_error_style_b(self):
        """Verify error handling with style 'b' matches baseline."""
        def failing_tool(x: int) -> int:
            raise RuntimeError("runtime problem")
        
        # Run baseline
        baseline_result = call_tool_b(failing_tool, "crash", {"x": 2})
        
        # Run enhanced
        from agent_tools_hook import invoke_single_tool
        enhanced_result_obj = invoke_single_tool(failing_tool, "crash", {"x": 2}, log_style="b")
        enhanced_result = enhanced_result_obj.to_dict()
        
        # Compare all fields
        self.assertEqual(baseline_result["tool_name"], enhanced_result["tool_name"])
        self.assertEqual(baseline_result["status"], "error")
        self.assertEqual(enhanced_result["status"], "error")
        self.assertEqual(baseline_result["error"], enhanced_result["error"])
        self.assertEqual(baseline_result["args"], enhanced_result["args"])
        self.assertIsNone(baseline_result["output"])
        self.assertIsNone(enhanced_result["output"])
        self.assertEqual(baseline_result["logs"], enhanced_result["logs"])
    
    def test_run_all_multiple_tools(self):
        """Verify run_all orchestration matches baseline exactly."""
        def add(x: int, y: int) -> int:
            return x + y
        
        def multiply(x: int, y: int) -> int:
            return x * y
        
        def subtract(x: int, y: int) -> int:
            return x - y
        
        tools = [add, multiply, subtract]
        names = ["add", "multiply", "subtract"]
        payloads = [{"x": 10, "y": 3}, {"x": 4, "y": 5}, {"x": 20, "y": 7}]
        
        # Run baseline
        baseline_results = run_all(tools, names, payloads)
        
        # Run enhanced
        enhanced_result_objs = run_all_tools(tools, names, payloads)
        enhanced_results = [r.to_dict() for r in enhanced_result_objs]
        
        # Compare length
        self.assertEqual(len(baseline_results), len(enhanced_results))
        
        # Compare each result
        for baseline, enhanced in zip(baseline_results, enhanced_results):
            self.assertEqual(baseline["tool_name"], enhanced["tool_name"])
            self.assertEqual(baseline["status"], enhanced["status"])
            self.assertEqual(baseline["error"], enhanced["error"])
            self.assertEqual(baseline["args"], enhanced["args"])
            self.assertEqual(baseline["output"], enhanced["output"])
            self.assertEqual(baseline["logs"], enhanced["logs"])
    
    def test_run_all_with_errors(self):
        """Verify run_all handles errors the same way as baseline."""
        def good_tool(x: int) -> int:
            return x * 2
        
        def bad_tool(x: int) -> int:
            raise ValueError("intentional error")
        
        tools = [good_tool, bad_tool, good_tool, bad_tool]
        names = ["good1", "bad1", "good2", "bad2"]
        payloads = [{"x": 5}, {"x": 10}, {"x": 15}, {"x": 20}]
        
        # Run baseline
        baseline_results = run_all(tools, names, payloads)
        
        # Run enhanced
        enhanced_result_objs = run_all_tools(tools, names, payloads)
        enhanced_results = [r.to_dict() for r in enhanced_result_objs]
        
        # Compare length
        self.assertEqual(len(baseline_results), len(enhanced_results))
        
        # Compare each result
        for idx, (baseline, enhanced) in enumerate(zip(baseline_results, enhanced_results)):
            self.assertEqual(baseline["tool_name"], enhanced["tool_name"], f"Mismatch at index {idx}")
            self.assertEqual(baseline["status"], enhanced["status"], f"Mismatch at index {idx}")
            self.assertEqual(baseline["error"], enhanced["error"], f"Mismatch at index {idx}")
            self.assertEqual(baseline["args"], enhanced["args"], f"Mismatch at index {idx}")
            self.assertEqual(baseline["output"], enhanced["output"], f"Mismatch at index {idx}")
            self.assertEqual(baseline["logs"], enhanced["logs"], f"Mismatch at index {idx}")
    
    def test_empty_invocation_list(self):
        """Verify empty input produces empty output in both implementations."""
        baseline_results = run_all([], [], [])
        enhanced_result_objs = run_all_tools([], [], [])
        enhanced_results = [r.to_dict() for r in enhanced_result_objs]
        
        self.assertEqual(len(baseline_results), 0)
        self.assertEqual(len(enhanced_results), 0)
    
    def test_alternating_log_styles(self):
        """Verify that log styles alternate correctly (a, b, a, b, ...)."""
        def identity(x: Any) -> Any:
            return x
        
        tools = [identity] * 4
        names = ["id0", "id1", "id2", "id3"]
        payloads = [{"x": i} for i in range(4)]
        
        # Run both implementations
        baseline_results = run_all(tools, names, payloads)
        enhanced_result_objs = run_all_tools(tools, names, payloads)
        enhanced_results = [r.to_dict() for r in enhanced_result_objs]
        
        # Verify alternating patterns in logs
        for idx, (baseline, enhanced) in enumerate(zip(baseline_results, enhanced_results)):
            if idx % 2 == 0:
                # Style 'a': "calling", "done"
                self.assertIn("calling", baseline["logs"][0])
                self.assertEqual("done", baseline["logs"][1])
            else:
                # Style 'b': "tool", "start", "ok"
                self.assertIn("tool", enhanced["logs"][0])
                self.assertIn("start", enhanced["logs"][0])
                self.assertEqual("ok", enhanced["logs"][1])
            
            # Logs should match exactly
            self.assertEqual(baseline["logs"], enhanced["logs"])


if __name__ == "__main__":
    unittest.main()
