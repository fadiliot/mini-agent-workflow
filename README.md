
# Mini Agent Workflow Engine

This project implements a minimal workflow / graph execution engine using FastAPI.  
The system allows defining a sequence of steps (nodes), routing between them, maintaining shared state, and running workflows via APIs.



## Project Structure


app/
  main.py              # FastAPI app and API routes
  engine.py            # Workflow / graph execution engine
  models.py            # Pydantic models
  tools.py             # Tool registry and node functions
  sample_workflow.py   # Example workflow
  logging_config.py    # Logging configuration




## How to Run

1. Install dependencies:
pip install fastapi uvicorn pydantic


2. Start the server:
uvicorn app.main:app --reload


The API will be available at:

[http://localhost:8000](http://localhost:8000)
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)



## What the Workflow Engine Supports

Nodes: Each node is a Python function that reads and updates a shared state dictionary.
Shared State: State flows from one node to the next and is mutated by each step.
Edges: Each node defines which node executes next.
Conditional Branching: Execution can branch based on values in the state.
Looping: Nodes can loop until a condition in the state is met.
Tool Registry: Tools (node functions) are registered and referenced by name.
Execution Logging: Each workflow run records step-by-step execution logs.

Workflows and runs are stored in memory for simplicity.


## Example Agent Workflow

The repository includes a Summarization + Refinement workflow:

1. Split input text into chunks
2. Generate short summaries for each chunk
3. Merge summaries
4. Refine the final summary
5. Loop until the summary length is below a threshold

The example is fully rule-based and demonstrates sequencing, branching, and looping.



## What I Would Improve With More Time

* Persist graphs and runs in a database instead of in-memory storage
* Background execution for long-running workflows
* WebSocket support for streaming execution logs
* More expressive branching conditions
* Retry and timeout handling per node

## Repository Contents

This repository contains:

- **FastAPI project**
  All application code is located inside the `/app` folder and exposes APIs to create and run workflows.

- **Graph Engine Implementation**  
  The core workflow / graph execution logic is implemented in `engine.py`, supporting nodes, shared state, branching, and looping.

- **Example Agent Workflow**  
  An example rule-based agent workflow is implemented in `sample_workflow.py` along with its supporting tools in `tools.py`.  
  This workflow demonstrates sequential execution, conditional branching, and looping.



