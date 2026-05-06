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

def send_response(state: AgentState) -> dict:
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
