from typing import Any, Callable, Dict, List


Tool = Callable[..., Any]


def call_tool_a(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Very small, repetitive baseline implementation for calling a tool.

    This function pretends to be part of an agent tool hook layer. It records
    a few pieces of information in a plain dict and calls the tool directly.
    The structure is intentionally simplistic and somewhat repetitive so it
    can be used as a baseline for enhancement tasks.
    """
    result: Dict[str, Any] = {
        "tool_name": name,
        "status": "ok",
        "error": None,
        "args": args,
        "output": None,
        "logs": [],  # type: ignore[list-item]
    }
    result["logs"].append(f"calling {name} with {args!r}")

    try:
        output = tool(**args)
    except Exception as exc:  # pragma: no cover - simple baseline behavior
        result["status"] = "error"
        result["error"] = str(exc)
        result["logs"].append(f"error: {exc}")
    else:
        result["output"] = output
        result["logs"].append("done")

    return result


def call_tool_b(tool: Tool, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    # This is deliberately very similar to call_tool_a, with tiny differences
    # in the log messages to simulate copy-pasted code that evolved over time.
    result: Dict[str, Any] = {
        "tool_name": name,
        "status": "ok",
        "error": None,
        "args": args,
        "output": None,
        "logs": [],  # type: ignore[list-item]
    }
    result["logs"].append(f"tool {name} start {args!r}")

    try:
        output = tool(**args)
    except Exception as exc:  # pragma: no cover
        result["status"] = "error"
        result["error"] = str(exc)
        result["logs"].append(f"failed: {exc}")
    else:
        result["output"] = output
        result["logs"].append("ok")

    return result


def run_all(tools: List[Tool], names: List[str], payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Very small orchestrator that uses the two baseline hook functions.

    It is intentionally simple and not very configurable: it just zips three
    lists and alternates between call_tool_a and call_tool_b.
    """
    results: List[Dict[str, Any]] = []
    for index, (tool, name, args) in enumerate(zip(tools, names, payloads)):
        if index % 2 == 0:
            results.append(call_tool_a(tool, name, args))
        else:
            results.append(call_tool_b(tool, name, args))
    return results
