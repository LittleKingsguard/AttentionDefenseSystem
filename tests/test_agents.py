import pytest
from typing import cast
from agents.supervisor import supervisor_node, supervisor_router
from agents.state import AgentState

def test_supervisor_router():
    state = cast(AgentState, {"next": "drafter"})
    assert supervisor_router(state) == "drafter"

def test_supervisor_node_fallback(monkeypatch):
    """Test the fallback logic when LLM is not configured."""
    # Ensure get_llm returns None
    monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # Test ticket routing
    state = {
        "incoming_message": "Ticket-404 status?",
        "requester": "Bob",
        "topic": None,
        "messages": [],
        "sender": "user",
        "requires_response": None,
        "drafted_response": None,
        "final_response": None,
        "next": "supervisor"
    }
    result = supervisor_node(cast(AgentState, state))
    assert result["next"] == "git_expert"
    assert result["topic"] == "Ticket-404"
    
    # Test general email routing
    state["incoming_message"] = "When is the meeting?"
    result = supervisor_node(cast(AgentState, state))
    assert result["next"] == "email_expert"
    
    # Test drafter routing when messages exist
    state["messages"] = ["Some previous context from experts"]
    result = supervisor_node(cast(AgentState, state))
    assert result["next"] == "drafter"
