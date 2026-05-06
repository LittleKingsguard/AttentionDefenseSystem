import os
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(__file__))

from agents import graph, AgentState
from db import init_db, insert_log
from ui import request_human_approval

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.example'))

app = FastAPI(title="Attention Defense System - A2A Node")

class HandshakeRequest(BaseModel):
    sender_id: str
    intent: str
    urgency: str
    payload: str
    signature: str

def process_a2a_message(sender_id: str, payload: str):
    print(f"\n[A2A Server] Processing incoming message from {sender_id}...")
    
    initial_state = AgentState(
        incoming_message=payload,
        requester=sender_id,
        topic=None,
        messages=[],
        sender="user",
        requires_response=None,
        drafted_response=None,
        final_response=None,
        next="supervisor"
    )
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run graph
    graph.invoke(initial_state, config)
        
    snapshot = graph.get_state(config)
    if snapshot.next and snapshot.next[0] == "human_approval":
        state = snapshot.values
        draft = state.get("drafted_response")
        
        insert_log("received", state['requester'], state.get('topic', 'A2A Message'), state['incoming_message'], None)
        
        # Note: In a production system, this GUI call needs to be dispatched to the main thread.
        # For this prototype, we call it directly.
        try:
            decision = request_human_approval(state['requester'], state['incoming_message'], draft)
            
            if decision and decision["action"] in ["approve", "edit"]:
                insert_log("sent", state['requester'], state.get('topic', 'A2A Message'), decision["content"], decision["action"])
                graph.update_state(config, {"final_response": decision["content"]})
                graph.invoke(None, config)
            else:
                insert_log("sent", state['requester'], state.get('topic', 'A2A Message'), "Message Rejected", "reject")
        except Exception as e:
            print(f"[A2A Server] Error showing UI: {e}")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/inbound/handshake", status_code=202)
async def inbound_handshake(request: HandshakeRequest, background_tasks: BackgroundTasks):
    """
    Receives an incoming A2A handshake. 
    Verifies the signature (mocked) and processes the payload asynchronously.
    """
    # Mock signature verification
    if not request.signature:
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # Process message in background to return 202 Accepted immediately
    background_tasks.add_task(process_a2a_message, request.sender_id, request.payload)
    
    return {"status": "Accepted", "message": "Handshake received and is being processed."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
