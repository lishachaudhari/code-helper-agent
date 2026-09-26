import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

CRITIC_PROMPT = """You are a code reviewer for an autonomous coding agent.

Task: {task}

The following code ran successfully with this output:
{output}

Code:
{code}

Review the code for:
1. Edge cases that might be missed
2. Readability or style issues
3. Whether it fully satisfies the original task

Respond ONLY with valid JSON in this exact format, no extra text, no markdown:
{{"quality": "good" or "needs_improvement", "notes": "1-2 sentence summary of your review"}}
"""

def review_code(state: dict) -> dict:
    """Reviews successful code for quality, updates state with reflection notes."""
    prompt = CRITIC_PROMPT.format(
        task=state["task"],
        output=state["test_results"]["output"],
        code=state["code"],
    )

    response = llm.invoke(prompt)
    raw_text = response.content.strip().replace("```json", "").replace("```", "").strip()

    try:
        review = json.loads(raw_text)
    except json.JSONDecodeError:
        review = {"quality": "good", "notes": raw_text}

    state["review"] = review
    state["history"] = state.get("history", [])
    state["history"].append({
        "stage": "critic",
        "output": review
    })

    return state