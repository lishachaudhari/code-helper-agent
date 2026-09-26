from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    task: str                      # the original user task
    plan: List[str]                # list of steps from the planner
    current_step_index: int        # which step we're on
    code: str                      # current code attempt
    test_results: Optional[dict]   # {"success": bool, "output": str, "error": str}
    iteration_count: int           # retries for current step
    max_iterations: int            # retry cap (e.g. 5)
    history: List[dict]            # log of every attempt for the final report
    final_output: Optional[str]    # compiled final answer
    review: Optional[dict] 