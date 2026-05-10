import os
import requests
from typing import List, Optional
from langchain_core.messages import HumanMessage
import sys

# Ensure we can import from agents
sys.path.append(os.path.dirname(__file__))
from agents.state import get_llm

DATALINK_URL = os.environ.get("DATALINK_URL", "http://localhost:8001")

def push_to_datalink(platform: str, channel_id: str, user_id: str, content: str):
    """
    Push a message or factual update to the Datalink service.
    """
    url = f"{DATALINK_URL}/ingest"
    payload = {
        "platform": platform,
        "channel_id": channel_id,
        "user_id": user_id,
        "content": content
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[DatalinkClient] Error pushing to datalink: {e}")
        return None

def query_datalink(query: str, top_k: int = 5, platform: Optional[str] = None):
    """
    Query the Datalink service for relevant context.
    """
    url = f"{DATALINK_URL}/query"
    payload = {
        "query": query,
        "top_k": top_k,
        "platform": platform
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[DatalinkClient] Error querying datalink: {e}")
        return []

def summarize_for_datalink(content: str) -> str:
    """
    Rewrites the provided content into a concise, impartial factual summary.
    Strips out personal tone, interaction preferences, and irrelevant conversational filler.
    """
    llm = get_llm()
    if not llm:
        return content # Fallback to original content if LLM is unavailable
        
    prompt = (
        "You are a factual summarization agent. Your task is to extract the core informational content "
        "from the following text and rewrite it into a concise, impartial, and factual summary. "
        "REMOVE all personal greetings, tone markers, interaction preferences, and conversational filler. "
        "Focus ONLY on the data, decisions, or status updates mentioned.\n\n"
        f"TEXT TO SUMMARIZE:\n{content}\n\n"
        "FACTUAL SUMMARY:"
    )
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_content = response.content
        if isinstance(raw_content, list):
            # Handle multi-modal content list if necessary
            final_content = " ".join([c if isinstance(c, str) else str(c) for c in raw_content])
        else:
            final_content = raw_content
        return final_content.strip()
    except Exception as e:
        print(f"[DatalinkClient] Error during summarization: {e}")
        return content
