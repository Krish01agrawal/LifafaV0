"""Mem0 Agent AGNO stub
Provides a fallback implementation of query_mem0 so the WebSocket server can start even when the
full Mem0 agent module is not yet integrated.

Replace this stub with the real integration once available.
"""
from typing import Any

async def query_mem0(user_id: str, query: str, *args: Any, **kwargs: Any) -> str:
    """Stub async function that mimics an LLM agent call.

    Parameters
    ----------
    user_id : str
        ID of the authenticated user making the request.
    query : str
        Natural-language query from the frontend.

    Returns
    -------
    str
        A placeholder response so the chat UI remains functional.
    """
    # TODO: Replace with actual Mem0 agent call.
    return (
        "📢 (Stub) The backend Mem0 agent is not configured yet. "
        "You asked: '{query}'. Integrate the real agent to get meaningful answers."
    ) 