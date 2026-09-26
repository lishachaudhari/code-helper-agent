import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

CODER_PROMPT = """You are a coding module for an autonomous agent.

Overall task: {task}

Plan so far:
{plan}

Write complete, runnable Python code that accomplishes the overall task.
Include the function definition AND a few example calls with print statements so the code can be executed and verified.

{error_context}

Respond ONLY with a single Python code block, no explanation before or after.
"""

ESCALATION_NOTICE = """
IMPORTANT: The last {count} attempts have FAILED. Here is what was tried and why each failed:

{failed_summary}

Do NOT repeat either of these approaches. Use a fundamentally different algorithm or strategy this time.
"""

def get_failed_attempts_summary(state: dict, last_n: int = 2) -> str:
    """Looks through history and summarizes the last N failed attempts
    (their code + the error they produced), so the Coder can avoid repeating them."""
    history = state.get("history", [])

    # Pull all executor entries that failed, most recent first
    failed_executor_entries = [
        h for h in history if h["stage"] == "executor" and not h["success"]
    ]
    failed_executor_entries = failed_executor_entries[-last_n:]

    if not failed_executor_entries:
        return ""

    summary_parts = []
    for entry in failed_executor_entries:
        iteration = entry["iteration"]
        # find the coder entry with the same iteration number
        matching_coder = next(
            (h for h in history if h["stage"] == "coder" and h["iteration"] == iteration - 1),
            None
        )
        code_snippet = matching_coder["output"] if matching_coder else "(code not found)"
        summary_parts.append(
            f"Attempt {iteration}:\nCode tried:\n{code_snippet}\nFailed because:\n{entry['error']}\n"
        )

    return "\n".join(summary_parts)

def extract_code(text: str) -> str:
    """Pulls code out of a markdown code block, or returns raw text if none found."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def write_code(state: dict) -> dict:
    """Generates code based on the plan and any previous error, updates state."""
    plan_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(state["plan"]))

    error_context = ""

    if state.get("iteration_count", 0) >= 2:
        # Escalation: summarize last 2 failures and demand a different approach
        failed_summary = get_failed_attempts_summary(state, last_n=2)
        error_context = ESCALATION_NOTICE.format(
            count=2,
            failed_summary=failed_summary
        )
    elif state.get("test_results") and not state["test_results"].get("success", True):
        # Normal retry: just show the most recent error
        error_context = f"""
Your previous attempt failed with this error:
{state['test_results'].get('error', 'Unknown error')}

Here was the previous code:
{state.get('code', '')}

Fix the issue and provide corrected code.
"""

    prompt = CODER_PROMPT.format(
        task=state["task"],
        plan=plan_text,
        error_context=error_context
    )

    response = llm.invoke(prompt)
    code = extract_code(response.content)

    state["code"] = code
    state["history"] = state.get("history", [])
    state["history"].append({
        "stage": "coder",
        "iteration": state.get("iteration_count", 0),
        "output": code
    })

    return state