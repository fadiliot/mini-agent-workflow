# app/models.py
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GraphNodeCreate(BaseModel):
    """
    Node definition as given by the client when creating a graph.
    Node IDs are the keys in the 'nodes' dict in GraphCreateRequest.
    """
    tool: str = Field(..., description="Name of the tool to run for this node")
    next: Optional[str] = Field(
        None, description="Default next node id if no branch matches"
    )
    branch_on: Optional[str] = Field(
        None,
        description="State key to branch on after this node runs; value is cast to str.",
    )
    branches: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Mapping from str(value) to next node id. If no match, 'next' is used.",
    )


class GraphCreateRequest(BaseModel):
    start_node: str
    nodes: Dict[str, GraphNodeCreate]


class GraphNode(BaseModel):
    """
    Internal node representation in the engine.
    """
    id: str
    tool: str
    next: Optional[str] = None
    branch_on: Optional[str] = None
    branches: Optional[Dict[str, Optional[str]]] = None


class GraphDefinition(BaseModel):
    id: str
    start_node: str
    nodes: Dict[str, GraphNode]


class RunStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class StepLog(BaseModel):
    step: int
    node_id: str
    tool: str
    state_snapshot: Dict[str, Any]


class RunState(BaseModel):
    id: str
    graph_id: str
    current_node: Optional[str]
    state: Dict[str, Any]
    log: List[StepLog] = []
    status: RunStatus = RunStatus.running
    error: Optional[str] = None


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[StepLog]
    status: RunStatus
    error: Optional[str] = None


class GraphCreateResponse(BaseModel):
    graph_id: str
