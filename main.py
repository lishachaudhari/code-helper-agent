from agent.graph import build_graph

def main():
    task = input("Enter a coding task: ")

    initial_state = {
        "task": task,
        "plan": [],
        "current_step_index": 0,
        "code": "",
        "test_results": None,
        "iteration_count": 0,
        "max_iterations": 5,
        "history": [],
        "final_output": None,
    }

    app = build_graph()
    final_state = app.invoke(initial_state)

    print("\n" + "=" * 50)
    print("FINAL RESULT")
    print("=" * 50)
    print(final_state["final_output"])

if __name__ == "__main__":
    main()