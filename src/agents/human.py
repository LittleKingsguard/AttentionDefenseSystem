import os
import requests
import sys

# Ensure we can import registry_client from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from registry_client import get_agent_address
from .state import AgentState

def human_approval(state: AgentState) -> dict:
    if not state.get("final_response"):
        return {"final_response": state.get("drafted_response")}
    return {}

def send_response(state: AgentState) -> AgentState:
    sender_id = os.environ.get("SENDER_ID", "local-agent-001")
    recipient_id = state['requester']
    message_content = state['final_response']
    
    # Try to discover recipient address from registry
    address = get_agent_address(recipient_id)
    
    if address:
        print(f"\n[SYSTEM] Discovered address for {recipient_id}: {address}")
        print(f"[SYSTEM] Sending A2A handshake to {address}...")
        
        try:
            payload = {
                "sender_id": sender_id,
                "intent": "response",
                "urgency": "normal",
                "payload": message_content,
                "signature": "mock-signature"
            }
            # Note: The endpoint path should match the one defined in server.py
            response = requests.post(f"{address}/inbound/handshake", json=payload, timeout=5)
            
            if response.status_code == 202:
                print(f"[SYSTEM] Message successfully delivered via A2A to {recipient_id}.")
            else:
                print(f"[SYSTEM] Registry found address, but delivery failed. Status: {response.status_code}")
                print(f"[SYSTEM] Fallback message content:\n{message_content}")
        except Exception as e:
            print(f"[SYSTEM] Error during outbound A2A communication: {e}")
            print(f"[SYSTEM] Fallback message content:\n{message_content}")
    else:
        # Fallback to console for mock data / local testing
        print(f"\n[SYSTEM] No registry entry found for {recipient_id}. Outputting to console:")
        print(f"--------------------------------------------------")
        print(f"TO: {recipient_id}")
        print(f"MESSAGE: {message_content}")
        print(f"--------------------------------------------------\n")
        
    return state

def datalink_ingest_node(state: AgentState) -> dict:
    """
    Optional node that rewrites the final interaction into a factual summary
    and pushes it to the Datalink store.
    """
    from datalink_client import push_to_datalink, summarize_for_datalink
    
    # We only ingest if there was a final response
    if state.get("final_response"):
        print(f"\n[SYSTEM] Preparing factual summary for Datalink...")
        
        # Combine incoming message and final response for full context
        full_interaction = f"Inbound from {state['requester']}: {state['incoming_message']}\nResponse: {state['final_response']}"
        
        # Summarize to strip personal tone/preferences
        factual_summary = summarize_for_datalink(full_interaction)
        
        # Push to datalink
        # Use 'a2a' as platform for interactions
        push_to_datalink(
            platform="a2a",
            channel_id=state.get("topic") or "general_interaction",
            user_id=state["requester"],
            content=factual_summary
        )
        print(f"[SYSTEM] Factual summary pushed to Datalink.")
        
    return {"next": "FINISH"}
