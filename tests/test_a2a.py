import pytest
from typing import cast
from unittest.mock import patch, MagicMock
from agents.human import send_response
from agents.state import AgentState

def test_send_response_outbound_discovery():
    """Test that send_response attempts an outbound POST when an address is found."""
    state = {
        "requester": "Agent-X",
        "final_response": "Hello Agent-X, here is the answer.",
        "incoming_message": "Question",
        "topic": "Test",
        "messages": [],
        "sender": "user",
        "requires_response": True,
        "drafted_response": "Hello Agent-X",
        "next": "send_response"
    }
    
    with patch("agents.human.get_agent_address") as mock_get_addr, \
         patch("agents.human.requests.post") as mock_post:
        
        mock_get_addr.return_value = "http://agent-x-endpoint:8001"
        mock_post.return_value.status_code = 202
        
        result = send_response(cast(AgentState, state))
        
        mock_get_addr.assert_called_once_with("Agent-X")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://agent-x-endpoint:8001/inbound/handshake"
        assert kwargs["json"]["payload"] == "Hello Agent-X, here is the answer."
        assert result == state

def test_send_response_fallback_to_console():
    """Test that send_response falls back to console when no address is found."""
    state = {
        "requester": "Unknown-Agent",
        "final_response": "Some content",
        "incoming_message": "Hi",
        "topic": "General",
        "messages": [],
        "sender": "user",
        "requires_response": True,
        "drafted_response": "Hi",
        "next": "send_response"
    }
    
    with patch("agents.human.get_agent_address") as mock_get_addr, \
         patch("agents.human.requests.post") as mock_post:
        
        mock_get_addr.return_value = None
        
        result = send_response(cast(AgentState, state))
        
        mock_get_addr.assert_called_once_with("Unknown-Agent")
        mock_post.assert_not_called()
        assert result == state
