from dataclasses import dataclass, field
from typing import Any

from agent.planner import PlanStep

@dataclass
class AgentState:
    messages: list[dict[str, Any]]
    iteration: int = 0

    plan: list[PlanStep] = field(default_factory=list)
    current_step: int = 0
    current_step_failures: int = 0
    replans: int = 0

    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)

    status: str = "running"