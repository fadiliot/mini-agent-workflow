# app/tools.py
from typing import Any, Dict, List

from .logging_config import setup_logger

logger = setup_logger("workflow.tools")


def split_text_into_chunks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    State in:
      - text: str
      - chunk_size: int (optional, default=200)

    State out:
      - chunks: List[str]
    """
    text: str = state.get("text", "")
    chunk_size: int = int(state.get("chunk_size", 200))

    logger.info(
        "split_text: text_length=%d chunk_size=%d",
        len(text),
        chunk_size,
    )

    chunks: List[str] = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])

    state["chunks"] = chunks

    logger.info(
        "split_text: chunks_created=%d",
        len(chunks),
    )

    return state


def summarize_chunks(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Naive summarization: take first N words of each chunk.
    State in:
      - chunks: List[str]
      - per_chunk_words: int (optional, default=30)

    State out:
      - summaries: List[str]
    """
    chunks: List[str] = state.get("chunks", [])
    per_chunk_words: int = int(state.get("per_chunk_words", 30))

    logger.info(
        "summarize_chunks: chunks=%d per_chunk_words=%d",
        len(chunks),
        per_chunk_words,
    )

    summaries: List[str] = []
    for chunk in chunks:
        words = chunk.split()
        short = " ".join(words[:per_chunk_words])
        summaries.append(short)

    state["summaries"] = summaries

    logger.info(
        "summarize_chunks: summaries_created=%d",
        len(summaries),
    )

    return state


def merge_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very simple merge: concatenate all summaries.
    State in:
      - summaries: List[str]

    State out:
      - merged_summary: str
    """
    summaries: List[str] = state.get("summaries", [])

    logger.info(
        "merge_summaries: summaries_count=%d",
        len(summaries),
    )

    merged = " ".join(summaries)
    state["merged_summary"] = merged

    logger.info(
        "merge_summaries: merged_length=%d",
        len(merged),
    )

    return state


def refine_summary_until_short(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refinement step, designed to be run in a loop.
    State in:
      - merged_summary or final_summary
      - length_limit: int (optional, default=400 chars)

    State out:
      - final_summary: str
      - summary_len: int
      - is_short_enough: bool (used for branching)
    """
    length_limit: int = int(state.get("length_limit", 400))

    summary: str = state.get("final_summary") or state.get("merged_summary", "")

    logger.info(
        "refine_summary: current_length=%d length_limit=%d",
        len(summary),
        length_limit,
    )

    if len(summary) > length_limit:
        summary = summary[:length_limit].rsplit(" ", 1)[0]

    state["final_summary"] = summary
    state["summary_len"] = len(summary)
    state["is_short_enough"] = len(summary) <= length_limit

    logger.info(
        "refine_summary: new_length=%d is_short_enough=%s",
        len(summary),
        state["is_short_enough"],
    )

    return state


TOOLS: Dict[str, Any] = {
    "split_text": split_text_into_chunks,
    "summarize_chunks": summarize_chunks,
    "merge_summaries": merge_summaries,
    "refine_summary": refine_summary_until_short,
}
