import os
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

class AgentState(TypedDict):
    incoming_message: str
    requester: str
    requires_response: bool
    topic: Optional[str]
    retrieved_context: Optional[str]
    drafted_response: Optional[str]
    final_response: Optional[str]

def get_llm():
    # If no key is set, we return None and use mock logic for the prototype
    if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "your_openai_api_key_here":
        return None
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

import json

def analyze_message(state: AgentState) -> AgentState:
    """Analyze if the message requires a status update and extract topic."""
    llm = get_llm()
    if not llm:
        # Mock logic
        msg = state["incoming_message"].lower()
        req_resp = "status" in msg or "update" in msg
        return {"requires_response": req_resp, "topic": "Ticket-404" if req_resp else "Other"}
    
    # Real LLM logic
    prompt = f"""Analyze the following message. Does it require a status update or information report? What is the main short topic (1-3 words, e.g. 'Ticket-404', 'Staging Deploy')?
Output ONLY a valid JSON object with two keys:
"requires_response": boolean
"topic": string

Message: {state['incoming_message']}"""
    response = llm.invoke([SystemMessage(content="You are a JSON-only message classifier."), HumanMessage(content=prompt)])
    try:
        # Strip codeblock formatting if present
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        data = json.loads(content)
        return {"requires_response": data.get("requires_response", False), "topic": data.get("topic", "General")}
    except Exception as e:
        requires_response = "true" in response.content.lower() or "yes" in response.content.lower()
        return {"requires_response": requires_response, "topic": "General"}

def retrieve_context(state: AgentState) -> AgentState:
    """Retrieve relevant context from the vector database."""
    from db import get_vector_store
    
    vector_store = get_vector_store()
    # Perform similarity search
    docs = vector_store.similarity_search(state["incoming_message"], k=3)
    
    if docs:
        context_str = "\n".join([f"- {d.page_content} (Source: {d.metadata.get('source', 'unknown')})" for d in docs])
    else:
        context_str = "No relevant context found."
        
    return {"retrieved_context": context_str}

def route_message(state: AgentState) -> str:
    if state.get("requires_response"):
        return "retrieve_context"
    return END

def draft_response(state: AgentState) -> AgentState:
    """Draft a response based on available context."""
    llm = get_llm()
    context = state.get("retrieved_context", "No context available.")
    
    if not llm:
        # Mock logic
        draft = f"Hello {state['requester']},\n\nRegarding your request, here is the current status based on my context:\n{context}\n\nLet me know if you need anything else."
        return {"drafted_response": draft}
    
    # Real LLM logic
    prompt = f"""You are a helpful assistant drafting a response for an employee.
Requester: {state['requester']}
Incoming Message: {state['incoming_message']}
Context available: {context}

Draft a professional response to the requester answering their inquiry using ONLY the provided context."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"drafted_response": response.content}

def human_approval(state: AgentState) -> AgentState:
    """
    This node serves as a breakpoint. 
    Execution will be interrupted BEFORE this node runs.
    When resumed, the state should contain the 'final_response' if edited, 
    or just use the drafted one.
    """
    if not state.get("final_response"):
        return {"final_response": state.get("drafted_response")}
    return {}

def send_response(state: AgentState) -> AgentState:
    """Send the final approved message."""
    print(f"\n[SYSTEM] Sending message to {state['requester']}:\n{state['final_response']}\n")
    return state

# Build the graph
builder = StateGraph(AgentState)
builder.add_node("analyze_message", analyze_message)
builder.add_node("retrieve_context", retrieve_context)
builder.add_node("draft_response", draft_response)
builder.add_node("human_approval", human_approval)
builder.add_node("send_response", send_response)

builder.set_entry_point("analyze_message")
builder.add_conditional_edges("analyze_message", route_message)
builder.add_edge("retrieve_context", "draft_response")
builder.add_edge("draft_response", "human_approval")
builder.add_edge("human_approval", "send_response")
builder.add_edge("send_response", END)

# Compile with a breakpoint before human approval
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["human_approval"])
