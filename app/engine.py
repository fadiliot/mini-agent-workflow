# app/engine.py
import inspect
import uuid
from typing import Any, Awaitable, Callable, Dict, Optional

from .models import (
    GraphDefinition,
    GraphNode,
    GraphNodeCreate,
    GraphCreateRequest,
    RunState,
    StepLog,
    RunStatus,
)

# app/engine.py
from app.logging_config import setup_logger

logger = setup_logger("workflow.engine")



ToolFunc = Callable[[Dict[str, Any]], Any]


class WorkflowEngine:
    """
    Very small in-memory workflow engine:
    - graphs: stored in-memory
    - runs: stored in-memory
    - nodes: reference "tools" by string name
    """

    def __init__(self, tools: Dict[str, ToolFunc]):
        self.tools = tools
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, RunState] = {}

    # ---------- Graph management ----------

    def create_graph(self, payload: GraphCreateRequest) -> str:
        graph_id = str(uuid.uuid4())

        nodes: Dict[str, GraphNode] = {}
        for node_id, node_def in payload.nodes.items():
            nodes[node_id] = GraphNode(
                id=node_id,
                tool=node_def.tool,
                next=node_def.next,
                branch_on=node_def.branch_on,
                branches=node_def.branches,
            )

        graph = GraphDefinition(
            id=graph_id,
            start_node=payload.start_node,
            nodes=nodes,
        )
        self.graphs[graph_id] = graph
        return graph_id

    def register_graph_object(self, graph: GraphDefinition) -> str:
        """
        Allow programmatic registration of a graph object,
        e.g. for a sample workflow.
        """
        self.graphs[graph.id] = graph
        return graph.id

    def get_graph(self, graph_id: str) -> GraphDefinition:
        if graph_id not in self.graphs:
            raise KeyError(f"Unknown graph_id: {graph_id}")
        return self.graphs[graph_id]

    # ---------- Run management / execution ----------

    async def run_graph(
        self,
        graph_id: str,
        initial_state: Dict[str, Any],
        max_steps: int = 100,
    ) -> RunState:
        graph = self.get_graph(graph_id)

        run_id = str(uuid.uuid4())
        run = RunState(
            id=run_id,
            graph_id=graph_id,
            current_node=graph.start_node,
            state=dict(initial_state),
            log=[],
            status=RunStatus.running,
        )
        self.runs[run_id] = run

        try:
            current_node_id: Optional[str] = graph.start_node
            step_counter = 0

            while current_node_id is not None:
                if step_counter >= max_steps:
                    raise RuntimeError("Max steps exceeded (possible infinite loop)")

                node = graph.nodes.get(current_node_id)
                if node is None:
                    raise RuntimeError(f"Node '{current_node_id}' not found in graph")

                tool = self.tools.get(node.tool)
                if tool is None:
                    raise RuntimeError(f"Tool '{node.tool}' not found in registry")

                # Run the tool (sync or async), passing and returning state dict
                result = tool(run.state)
                if inspect.isawaitable(result):
                    result = await result  # type: ignore[assignment]

                if not isinstance(result, dict):
                    raise RuntimeError(
                        f"Tool '{node.tool}' must return a dict (state), "
                        f"got {type(result)}"
                    )

                run.state = result
                step_counter += 1

                # Log snapshot (shallow copy)
                run.log.append(
                    StepLog(
                        step=step_counter,
                        node_id=node.id,
                        tool=node.tool,
                        state_snapshot=dict(run.state),
                    )
                )

                # Decide next node
                next_node_id: Optional[str]
                if node.branch_on:
                    value = run.state.get(node.branch_on)
                    key = str(value)
                    if node.branches and key in node.branches:
                        next_node_id = node.branches[key]
                    else:
                        next_node_id = node.next
                else:
                    next_node_id = node.next

                current_node_id = next_node_id
                run.current_node = current_node_id

            run.status = RunStatus.completed

        except Exception as e:
            run.status = RunStatus.failed
            run.error = str(e)

        return run

    def get_run(self, run_id: str) -> RunState:
        if run_id not in self.runs:
            raise KeyError(f"Unknown run_id: {run_id}")
        return self.runs[run_id]
