from .state import AgentState

def human_approval(state: AgentState) -> dict:
    if not state.get("final_response"):
        return {"final_response": state.get("drafted_response")}
    return {}

def send_response(state: AgentState) -> dict:
    print(f"\n[SYSTEM] Sending message to {state['requester']}:\n{state['final_response']}\n")
    return state
