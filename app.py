import streamlit as st
from agent.graph import build_graph

st.set_page_config(page_title="Code Helper Agent", page_icon="", layout="wide")

st.title("Code Helper Agent")
st.caption("An autonomous agent that plans, writes, executes, and self-corrects code — built with LangGraph + Groq")

task = st.text_area(
    "Enter a coding task:",
    placeholder="e.g. Write a function that checks if a number is prime",
    height=80,
)

max_iterations = st.slider("Max retry attempts", min_value=1, max_value=8, value=5)

run_button = st.button("Run Agent", type="primary")

if run_button and task.strip():
    initial_state = {
        "task": task,
        "plan": [],
        "current_step_index": 0,
        "code": "",
        "test_results": None,
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "history": [],
        "final_output": None,
        "review": None,
    }

    with st.spinner("Agent is working..."):
        app = build_graph()
        final_state = app.invoke(initial_state)

    st.divider()
    st.subheader("📋 Plan")
    for i, step in enumerate(final_state["plan"], 1):
        st.write(f"{i}. {step}")

    st.divider()
    st.subheader("🔄 Iteration Trace")
    for entry in final_state["history"]:
        stage = entry["stage"].upper()
        if stage == "PLANNER":
            continue
        elif stage == "CODER":
            with st.expander(f"🧑‍💻 CODER — attempt {entry.get('iteration', '?')}"):
                st.code(entry["output"], language="python")
        elif stage == "EXECUTOR":
            status = "✅ PASSED" if entry["success"] else "❌ FAILED"
            with st.expander(f"⚙️ EXECUTOR — {status} (iteration {entry['iteration']})"):
                if entry["success"]:
                    st.text(entry["output"])
                else:
                    st.error(entry["error"])
        elif stage == "CRITIC":
            review = entry["output"]
            icon = "✅" if review.get("quality") == "good" else "⚠️"
            st.info(f"{icon} **Critic verdict:** {review.get('quality')} — {review.get('notes')}")

    st.divider()
    st.subheader("🏁 Final Result")
    success = final_state["test_results"]["success"]
    if success:
        st.success(f"Task solved in {final_state['iteration_count']} iteration(s).")
    else:
        st.error(f"Failed after {final_state['iteration_count']} iteration(s).")

    st.code(final_state["code"], language="python")
    st.text("Output:")
    st.text(final_state["test_results"]["output"] or final_state["test_results"]["error"])

elif run_button:
    st.warning("Please enter a task first.")