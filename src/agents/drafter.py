from langchain_core.messages import HumanMessage, AIMessage
from .state import AgentState, get_llm
import sys
import os

# Ensure we can import registry_client from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from registry_client import get_interaction_skills

def drafter_node(state: AgentState) -> dict:
    llm = get_llm()
    if not llm:
        print("[WARNING] LLM not configured. Using mock drafted response.")
        draft = f"Hello {state['requester']},\n\nHere is a drafted response based on the expert findings.\n\nBest."
        return {"drafted_response": draft, "requires_response": True, "next": "human_approval"}
        
    prompt = f"You are a professional assistant drafting an email/message to '{state['requester']}'.\n"
    
    skills = get_interaction_skills(state['requester'])
    if skills:
        prompt += f"--- INTERACTION PREFERENCES ---\n"
        prompt += f"Tone Preference: {skills.get('tone_preference', 'Professional')}\n"
        if skills.get('rules'):
            prompt += "Rules:\n" + "\n".join(f"- {r}" for r in skills['rules']) + "\n"
        prompt += "-------------------------------\n\n"
        
    prompt += f"Incoming Message: {state['incoming_message']}\n\n"
    prompt += "Below are the findings from the domain experts:\n"
    
    for m in state.get("messages", []):
        if isinstance(m, AIMessage) and m.content:
            prompt += f"\n[{m.name or 'Expert'}]: {m.content}"
            
    prompt += "\nDraft a polite, cohesive, professional response to the requester using ONLY the provided findings. Follow the INTERACTION PREFERENCES if any are provided."
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"drafted_response": response.content, "requires_response": True, "next": "human_approval"}
