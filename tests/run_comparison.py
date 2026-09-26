import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.baseline import one_shot_solve
from agent.coder import extract_code
from agent.executor import run_code
from agent.graph import build_graph

# A small, fixed set of tasks — increasing difficulty
TASKS = [
    "Write a function that checks if a number is prime",
    "Write a function that returns the nth Fibonacci number using memoization",
    "Implement a stack-based calculator that evaluates expressions with +, -, *, /, and parentheses, respecting operator precedence",
    "Implement a rate limiter class using the token bucket algorithm, with a method to check if a request is allowed and unit tests demonstrating throttling behavior",
    "Write a function that merges overlapping intervals from a list of [start, end] pairs, handling unsorted input and edge cases like fully nested intervals",
    "Implement a LRU (least recently used) cache class with get and put methods that operate in O(1) time",
]

def test_baseline(task: str) -> bool:
    raw = one_shot_solve(task)
    code = extract_code(raw)
    fake_state = {"code": code}
    result = run_code(fake_state)
    return result["test_results"]["success"]

def test_agent(task: str) -> tuple[bool, int, str]:
    app = build_graph()
    initial_state = {
        "task": task, "plan": [], "current_step_index": 0, "code": "",
        "test_results": None, "iteration_count": 0, "max_iterations": 5,
        "history": [], "final_output": None, "review": None,
    }
    final_state = app.invoke(initial_state)
    quality = final_state.get("review", {}).get("quality", "n/a")
    return final_state["test_results"]["success"], final_state["iteration_count"], quality

def main():
    print(f"{'Task':<60} {'Baseline':<10} {'Agent':<10} {'Iter':<6} {'Quality'}")
    print("-" * 105)

    baseline_wins = 0
    agent_wins = 0

    for task in TASKS:
        baseline_success = test_baseline(task)
        agent_success, iterations, quality = test_agent(task)

        baseline_wins += baseline_success
        agent_wins += agent_success

        short_task = (task[:55] + "...") if len(task) > 55 else task
        print(f"{short_task:<60} {'PASS' if baseline_success else 'FAIL':<10} {'PASS' if agent_success else 'FAIL':<10} {iterations:<6} {quality}")

    print("-" * 105)
    print(f"Baseline success rate: {baseline_wins}/{len(TASKS)}")
    print(f"Agent success rate:    {agent_wins}/{len(TASKS)}")

if __name__ == "__main__":
    main()