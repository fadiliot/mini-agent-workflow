# app/main.py
from fastapi import FastAPI, HTTPException

from .engine import WorkflowEngine
from .logging_config import setup_logger
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    RunState,
)
from .sample_workflow import create_summarization_workflow
from .tools import TOOLS

app = FastAPI(title="Mini Agent Workflow Engine")

logger = setup_logger("workflow.api")

# Initialize engine + register sample workflow
engine = WorkflowEngine(tools=TOOLS)
sample_graph = create_summarization_workflow()
SAMPLE_GRAPH_ID = engine.register_graph_object(sample_graph)


@app.get("/")
def root():
    logger.info("GET / called")
    return {
        "message": "Mini agent workflow engine",
        "sample_graph_id": SAMPLE_GRAPH_ID,
    }


# ---------- Graph endpoints ----------

@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(payload: GraphCreateRequest):
    logger.info(
        "POST /graph/create start_node=%s node_count=%d",
        payload.start_node,
        len(payload.nodes),
    )
    try:
        graph_id = engine.create_graph(payload)
        logger.info("Graph created via API graph_id=%s", graph_id)
        return GraphCreateResponse(graph_id=graph_id)
    except Exception as e:
        logger.exception("Error in /graph/create: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(payload: GraphRunRequest):
    logger.info(
        "POST /graph/run graph_id=%s initial_state_keys=%s",
        payload.graph_id,
        list(payload.initial_state.keys()),
    )
    try:
        run = await engine.run_graph(
            graph_id=payload.graph_id,
            initial_state=payload.initial_state,
        )
        logger.info(
            "Run finished via API run_id=%s status=%s",
            run.id,
            run.status,
        )
    except KeyError as e:
        logger.exception("Not found in /graph/run: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error in /graph/run: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    return GraphRunResponse(
        run_id=run.id,
        final_state=run.state,
        log=run.log,
        status=run.status,
        error=run.error,
    )


@app.get("/graph/state/{run_id}", response_model=RunState)
def get_run_state(run_id: str):
    """
    Returns the full RunState (including current status and latest state).
    Works for both ongoing and completed runs.
    """
    logger.info("GET /graph/state/%s", run_id)
    try:
        run = engine.get_run(run_id)
        return run
    except KeyError as e:
        logger.exception("Not found in /graph/state: %s", e)
        raise HTTPException(status_code=404, detail=str(e))
