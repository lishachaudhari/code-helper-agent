import subprocess
import sys
import tempfile
import os

TIMEOUT_SECONDS = 10

# Build an absolute path to the sandbox folder, relative to this file's location,
# and create it if it doesn't exist (works both locally and on Streamlit Cloud)
SANDBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sandbox")
SANDBOX_DIR = os.path.abspath(SANDBOX_DIR)
os.makedirs(SANDBOX_DIR, exist_ok=True)


def run_code(state: dict) -> dict:
    """Executes state['code'] in an isolated subprocess and records the result."""
    code = state["code"]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=SANDBOX_DIR, encoding="utf-8"
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