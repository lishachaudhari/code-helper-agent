import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.planner import plan_task

state = {
    "task": "Write a Python function that checks if a number is prime",
}

result = plan_task(state)
print("Generated plan:")
for i, step in enumerate(result["plan"], 1):
    print(f"{i}. {step}")