from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.planner import plan_task
from agent.coder import write_code
from agent.executor import run_code
from agent.critic import review_code

def traced(label, fn):
    """Wraps a node function to print a labeled trace line before/after it runs."""
    def wrapper(state):
        print(f"\n[{label}] running...")
        result = fn(state)
        if label == "PLANNER":
            print(f"[{label}] plan: {result['plan']}")
        elif label == "CODER":
            print(f"[{label}] generated {len(result['code'].splitlines())} lines of code")
        elif label == "EXECUTOR":
            status = "PASSED" if result["test_results"]["success"] else "FAILED"
            print(f"[{label}] result: {status} (iteration {result['iteration_count']})")
            if not result["test_results"]["success"]:
                print(f"[{label}] error: {result['test_results']['error'][:200]}")
        elif label == "CRITIC":
            print(f"[{label}] verdict: {result['review'].get('quality')} — {result['review'].get('notes')}")
        return result
    return wrapper

def format_final_output(state: dict) -> dict:
    """Compiles the final answer once the loop ends (success or max retries)."""
    success = state["test_results"]["success"]

    if success:
        review = state.get("review", {})
        summary = (
            f"Task solved in {state['iteration_count']} iteration(s).\n\n"
            f"Final code:\n{state['code']}\n\n"
            f"Test output:\n{state['test_results']['output']}\n\n"
            f"Self-review: {review.get('notes', 'N/A')}"
        )
    else:
        summary = (
            f"Failed to solve the task after {state['iteration_count']} iteration(s).\n\n"
            f"Last code attempt:\n{state['code']}\n\n"
            f"Last error:\n{state['test_results']['error']}"
        )

    state["final_output"] = summary
    return state


def should_retry(state: dict) -> str:
    """Conditional edge: decides whether to retry, give up, or move to review."""
    success = state["test_results"]["success"]
    max_reached = state["iteration_count"] >= state["max_iterations"]

    if success:
        return "review"
    elif max_reached:
        return "give_up"
    else:
        return "retry"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", traced("PLANNER", plan_task))
    graph.add_node("coder", traced("CODER", write_code))
    graph.add_node("executor", traced("EXECUTOR", run_code))
    graph.add_node("critic", traced("CRITIC", review_code))
    graph.add_node("finalize", format_final_output)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "executor")

    graph.add_conditional_edges(
        "executor",
        should_retry,
        {
            "retry": "coder",
            "give_up": "finalize",
            "review": "critic",
        },
    )

    graph.add_edge("critic", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()