import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.coder import write_code, get_failed_attempts_summary

# Manually construct a state as if 2 attempts already failed
fake_state = {
    "task": "Write a function that reverses a linked list",
    "plan": ["Define a Node class", "Write an iterative reversal function", "Test it"],
    "iteration_count": 2,
    "test_results": {
        "success": False,
        "output": "",
        "error": "AttributeError: 'NoneType' object has no attribute 'next'"
    },
    "code": "def reverse(head):\n    while head.next:\n        head = head.next",
    "history": [
        {
            "stage": "coder",
            "iteration": 0,
            "output": "def reverse_recursive(head):\n    if not head:\n        return None\n    # buggy recursive attempt\n    return reverse_recursive(head.next)"
        },
        {
            "stage": "executor",
            "iteration": 1,
            "success": False,
            "output": "",
            "error": "RecursionError: maximum recursion depth exceeded"
        },
        {
            "stage": "coder",
            "iteration": 1,
            "output": "def reverse(head):\n    while head.next:\n        head = head.next"
        },
        {
            "stage": "executor",
            "iteration": 2,
            "success": False,
            "output": "",
            "error": "AttributeError: 'NoneType' object has no attribute 'next'"
        },
    ]
}

# First, just check the summary function works correctly
print("=== Failed attempts summary ===")
print(get_failed_attempts_summary(fake_state, last_n=2))
print("\n=== Now generating new code with escalation ===\n")

result = write_code(fake_state)
print(result["code"])