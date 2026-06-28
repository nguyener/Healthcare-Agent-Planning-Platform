from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class PlanStep(BaseModel):
    """
    Represents a single step in a plan.
    """
    name: str
    tool: str
    reason: str
    args: Dict[str, Any] = {}
    status: Literal["pending", "completed", "failed", "skipped"] = "pending"

class AgentPlan(BaseModel):
    """
    Represents a plan consisting of multiple steps for an agent to execute.
    """
    goal: str
    steps: List[PlanStep]

class ToolResult(BaseModel):
    """
    Represents the result of executing a tool in a plan step.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 

    

class ToolResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None    