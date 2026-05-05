import os
from typing import TypedDict, Annotated, Optional, Literal, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from db import get_vector_store

@tool
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for context. Useful for looking up tickets, emails, git commits, or scheduling information."""
    vector_store = get_vector_store()
    try:
        docs = vector_store.similarity_search(query, k=5)
        if docs:
            return "\n\n".join([f"--- Source: {d.metadata.get('source', 'unknown')} ---\n{d.page_content}" for d in docs])
        return "No relevant context found."
    except Exception as e:
        return f"Error searching knowledge base: {e}"

tools = [search_knowledge_base]

class AgentState(TypedDict):
    incoming_message: str
    requester: str
    topic: Optional[str]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    sender: str
    requires_response: Optional[bool]
    drafted_response: Optional[str]
    final_response: Optional[str]
    next: str

class Route(BaseModel):
    next: Literal["git_expert", "email_expert", "drafter", "FINISH"] = Field(
        description="The next agent to route to, or FINISH if no response is needed."
    )
    topic: str = Field(
        description="A short 1-3 word topic classification for the request."
    )

def get_llm():
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    model_name = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
    
    if provider == "openai":
        if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "your_openai_api_key_here":
            return None
        return ChatOpenAI(model=model_name, temperature=0)
        
    elif provider == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") == "your_anthropic_api_key_here":
            return None
        return ChatAnthropic(model=model_name, temperature=0)
        
    elif provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model_name, base_url=base_url, temperature=0)
        
    return None
