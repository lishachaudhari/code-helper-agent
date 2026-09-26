# Code Helper Agent

An autonomous coding agent built with LangGraph that plans, writes, executes, and self-corrects code through a structured Plan → Act → Observe → Reflect workflow — not a single LLM call.

## Problem Statement

Given a coding task in plain English, the agent:
1. Breaks it into a sequence of logical steps (planning)
2. Writes code for the task
3. Executes the code in a sandboxed environment and captures pass/fail results
4. If it fails, retries with the error fed back as context — and after 2 consecutive failures, escalates to a fundamentally different approach instead of patching the same one
5. Once it passes, performs a self-review for code quality (edge cases, readability, robustness)
6. Returns a final, coherent report: the working code, test output, and quality notes

## Architecture

```
User Task
   ↓
[Planner]  — breaks task into steps (LLM call)
   ↓
[Coder]    — writes code for the task (LLM call)
   ↓
[Executor] — runs code in a sandboxed subprocess, captures result
   ↓
 (conditional edge)
   ├── FAIL, retries remaining  → back to [Coder] (with error context; after 2 fails, escalation notice forces a new approach)
   ├── FAIL, retries exhausted  → [Finalize] (reports failure)
   └── PASS                     → [Critic] — reviews code quality (LLM call)
                                       ↓
                                  [Finalize] — compiles final report
```

This follows a **Plan-and-Execute + ReAct hybrid** pattern, implemented as a LangGraph `StateGraph` with a conditional edge driving the retry loop.

### Design decisions

- **Subprocess execution, not `exec()`**: isolates crashes/infinite loops from the main agent process. A 10-second timeout prevents runaway code from hanging the agent.
- **Escalation after 2 failures**: rather than naive retry-on-error, the agent summarizes what was tried and why it failed across the last 2 attempts, and explicitly instructs the model to use a different algorithm/strategy rather than patch the same one. This was tested directly with a synthetic failure history (`tests/test_escalation.py`) and confirmed to produce a genuinely different approach on the next attempt (a buggy recursive linked-list reversal and a buggy iterative attempt were both correctly summarized, and the agent's next attempt used a correct three-pointer iterative approach it hadn't tried before).
- **Separate Critic step**: quality review (edge cases, readability) is decoupled from correctness (tests passing). A one-shot LLM call has no mechanism to catch or report the kind of subtle issues (e.g., mutable default arguments, missing input validation, thread-safety gaps) that this step surfaces.
- **Max iteration cap**: retries are bounded (default 5) so a stubborn bug can't loop forever; this is reported transparently in the final output if the cap is hit.

## Tech Stack

- Python
- LangGraph (orchestration)
- Groq API (`openai/gpt-oss-120b`) — free tier, no cost, used per contest guidance encouraging free/open-source models
- `python-dotenv` for config

## Setup & Run Instructions

1. Clone the repo and navigate into it:
   ```bash
   git clone https://github.com/lishachaudhari/code-helper-agent
   cd code-helper-agent
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Add your Groq API key to a `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   ```
   (Get a free key at console.groq.com)
5. Run the agent:
   ```bash
   python main.py
   ```
   You'll be prompted to enter a coding task.

## Sample Input/Output

**Input:**
```
Write a function that returns the nth Fibonacci number using memoization
```

**Output (abbreviated):**
```
[PLANNER] plan: ['Define the function signature that accepts an integer n and an optional cache for memoization', 'Initialize the cache with base cases: Fibonacci(0) = 0 and Fibonacci(1) = 1', 'Check if n is in the cache; if so, return the cached value to avoid recomputation', 'If n is not cached, recursively compute Fibonacci(n-1) and Fibonacci(n-2), store the sum in the cache, and return it']

[CODER] generated 21 lines of code

[EXECUTOR] result: PASSED (iteration 1)

[CRITIC] verdict: needs_improvement — correctly computes Fibonacci numbers with memoization, but lacks handling for negative inputs (which would cause infinite recursion) and could use functools.lru_cache for simplicity.

FINAL RESULT
Task solved in 1 iteration(s).
[full function implementation, tested with F(0) through F(9), plus F(35) to demonstrate memoization efficiency on a larger input]
```

## Baseline Comparison (Agent vs. One-Shot LLM)

To validate the value of the agentic architecture, the same tasks were run through (a) a single one-shot LLM call with no planning/retry/review, and (b) the full agent pipeline.

| Task | Baseline | Agent | Iterations | Agent Quality Check |
|---|---|---|---|---|
| Prime check | PASS | PASS | 1 | good |
| Fibonacci (memoized) | PASS | PASS | 1 | needs_improvement |
| Stack-based calculator | PASS | PASS | 1 | needs_improvement |
| Token bucket rate limiter | PASS | PASS | 1 | needs_improvement |
| Merge overlapping intervals | PASS | PASS | 1 | good |
| LRU cache | PASS | PASS | 1 | good |

**Finding:** With a strong underlying model, both approaches achieve high correctness on these tasks — pass/fail alone does not differentiate them. The meaningful difference is **quality visibility**: the agent's Critic step flagged real issues (mutable default arguments, missing input validation, thread-safety gaps, shadowed builtin names) in 4 of 6 cases. The one-shot baseline has no mechanism to detect or surface these — it ships the same latent bugs silently. This demonstrates the agent's value is not limited to correctness recovery; it also produces an actionable self-assessment the baseline structurally cannot.

Run this comparison yourself:
```bash
python tests/run_comparison.py
```
code-helper-agent/
├── agent/
│   ├── state.py        # shared AgentState schema
│   ├── planner.py      # breaks task into steps
│   ├── coder.py         # writes/fixes code, includes escalation logic
│   ├── executor.py     # sandboxed code execution
│   ├── critic.py       # code quality review
│   ├── baseline.py     # one-shot comparison baseline
│   └── graph.py         # LangGraph StateGraph wiring
├── tests/
│   ├── test_planner.py
│   ├── test_coder.py
│   ├── test_executor.py
│   ├── test_critic.py
│   ├── test_escalation.py
│   └── run_comparison.py
├── sandbox/             # temp files for code execution (auto-cleaned)
├── main.py
├── requirements.txt
└── README.md
```

## Future Improvements

- [ ] Generate proper unit tests (e.g., via `pytest`) instead of relying on print-statement verification for pass/fail
- [ ] Support multi-file projects instead of single-function tasks
- [ ] Run multiple candidate solutions in parallel and pick the best one
- [ ] Persist run history to disk (JSON logs) for auditing past agent runs
