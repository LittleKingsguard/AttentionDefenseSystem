from langchain_core.messages import HumanMessage, AIMessage
from .state import AgentState, get_llm

def drafter_node(state: AgentState) -> dict:
    llm = get_llm()
    if not llm:
        print("[WARNING] LLM not configured. Using mock drafted response.")
        draft = f"Hello {state['requester']},\n\nHere is a drafted response based on the expert findings.\n\nBest."
        return {"drafted_response": draft, "requires_response": True, "next": "human_approval"}
        
    prompt = f"""You are a professional assistant drafting an email/message to '{state['requester']}'.
Incoming Message: {state['incoming_message']}

Below are the findings from the domain experts:
"""
    for m in state.get("messages", []):
        if isinstance(m, AIMessage) and m.content:
            prompt += f"\n[{m.name or 'Expert'}]: {m.content}"
            
    prompt += "\nDraft a polite, cohesive, professional response to the requester using ONLY the provided findings."
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"drafted_response": response.content, "requires_response": True, "next": "human_approval"}
