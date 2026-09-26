import subprocess
import sys
import tempfile
import os

TIMEOUT_SECONDS = 10

def run_code(state: dict) -> dict:
    """Executes state['code'] in an isolated subprocess and records the result."""
    code = state["code"]

    # Write code to a temporary file so we can run it as a real subprocess
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="sandbox", encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(code)
        tmp_path = tmp_file.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        success = result.returncode == 0
        test_results = {
            "success": success,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if not success else "",
        }

    except subprocess.TimeoutExpired:
        test_results = {
            "success": False,
            "output": "",
            "error": f"Execution timed out after {TIMEOUT_SECONDS} seconds (possible infinite loop).",
        }

    finally:
        # clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    state["test_results"] = test_results
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    state["history"] = state.get("history", [])
    state["history"].append({
        "stage": "executor",
        "iteration": state["iteration_count"],
        "success": test_results["success"],
        "output": test_results["output"],
        "error": test_results["error"],
    })

    return state