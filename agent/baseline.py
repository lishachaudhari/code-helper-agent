import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

BASELINE_PROMPT = """Write complete, runnable Python code for the following task.
Include example calls with print statements so the code can be executed and verified.

Task: {task}

Respond ONLY with a single Python code block, no explanation before or after.
"""

def one_shot_solve(task: str) -> str:
    """Single LLM call, no planning, no retry, no review — the baseline to compare against."""
    prompt = BASELINE_PROMPT.format(task=task)
    response = llm.invoke(prompt)
    return response.content