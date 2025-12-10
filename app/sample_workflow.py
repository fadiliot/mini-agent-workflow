# app/sample_workflow.py
from .models import GraphDefinition, GraphNode


def create_summarization_workflow(
    graph_id: str = "sample_summarization",
) -> GraphDefinition:
    """
    Workflow:
      1. split  -> split_text
      2. summarize -> summarize_chunks
      3. merge -> merge_summaries
      4. refine -> refine_summary (loop until is_short_enough == True)

    Branching / looping:
      - refine node sets state["is_short_enough"]
      - branch_on = "is_short_enough"
      - branches:
          "False" -> "refine"  (loop)
      - if True -> no branch match, next=None => workflow ends
    """
    nodes = {
        "split": GraphNode(
            id="split",
            tool="split_text",
            next="summarize",
        ),
        "summarize": GraphNode(
            id="summarize",
            tool="summarize_chunks",
            next="merge",
        ),
        "merge": GraphNode(
            id="merge",
            tool="merge_summaries",
            next="refine",
        ),
        "refine": GraphNode(
            id="refine",
            tool="refine_summary",
            next=None,
            branch_on="is_short_enough",
            branches={
                "False": "refine",  # loop until is_short_enough becomes True
            },
        ),
    }

    return GraphDefinition(
        id=graph_id,
        start_node="split",
        nodes=nodes,
    )
