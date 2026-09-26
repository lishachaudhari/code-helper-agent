import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0.3,
# )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

PLANNER_PROMPT = """You are a planning module for a coding agent.
Given a coding task, break it down into 3 to 5 clear, ordered steps needed to solve it.

Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
{{"steps": ["step 1 description", "step 2 description", "step 3 description"]}}

Task: {task}
"""

def plan_task(state: dict) -> dict:
    """Takes the AgentState, calls the LLM to generate a plan, updates state."""
    prompt = PLANNER_PROMPT.format(task=state["task"])
    response = llm.invoke(prompt)

    raw_text = response.content.strip()
    # strip accidental markdown fences if the model adds them
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw_text)
        steps = parsed.get("steps", [])
    except json.JSONDecodeError:
        # fallback: treat the whole response as a single step if parsing fails
        steps = [raw_text]

    state["plan"] = steps
    state["current_step_index"] = 0
    state["iteration_count"] = 0
    state["history"] = state.get("history", [])
    state["history"].append({
        "stage": "planner",
        "output": steps
    })

    return state