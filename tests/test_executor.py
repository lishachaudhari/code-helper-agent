import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.planner import plan_task
from agent.coder import write_code
from agent.executor import run_code

state = {
    "task": "Write a Python function that checks if a number is prime",
}

state = plan_task(state)
state["test_results"] = None
state["iteration_count"] = 0

state = write_code(state)
state = run_code(state)

print("Success:", state["test_results"]["success"])
print("\n--- Output ---")
print(state["test_results"]["output"])
print("\n--- Error ---")
print(state["test_results"]["error"])