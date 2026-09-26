import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.planner import plan_task
from agent.coder import write_code

state = {
    "task": "Write a Python function that checks if a number is prime",
}

state = plan_task(state)
state["test_results"] = None
state["iteration_count"] = 0

state = write_code(state)

print("Generated code:\n")
print(state["code"])