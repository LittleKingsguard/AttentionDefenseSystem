import uuid
import os
from dotenv import load_dotenv
from agent import graph, AgentState
from db import init_db, insert_log
from ui import request_human_approval

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

def main():
    # Initialize the relational database tables
    init_db()
    
    print("=============================================")
    print(" Attention Defense System - Prototype v0.1 ")
    print("=============================================\n")
    
    print("Simulating an incoming message from a manager...")
    
    # Mock data
    requester = "Manager Bob"
    incoming_message = "Can I get a quick status update on the production defect (Ticket-404)?"
    
    print(f"From: {requester}")
    print(f"Message: '{incoming_message}'\n")
    
    initial_state = AgentState(
        incoming_message=incoming_message,
        requester=requester,
        requires_response=None,
        topic=None,
        retrieved_context=None,
        drafted_response=None,
        final_response=None
    )
    
    # Run the graph with a specific thread_id to support memory/breakpoints
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("--- Agent is processing the incoming message ---")
    for event in graph.stream(initial_state, config):
        for key, value in event.items():
            print(f"Node finished: {key}")
            
    # Check if the graph paused for human approval
    snapshot = graph.get_state(config)
    if snapshot.next and snapshot.next[0] == "human_approval":
        state = snapshot.values
        draft = state.get("drafted_response")
        
        print("\n=== HUMAN APPROVAL REQUIRED ===")
        print("Opening desktop notification UI...")
        
        # Log the received message now that we have extracted the topic
        insert_log("received", state['requester'], state.get('topic', 'General'), state['incoming_message'], None)
        
        # Open the UI window and block until a decision is made
        decision = request_human_approval(state['requester'], state['incoming_message'], draft)
        
        # Log the outgoing decision to database
        if decision and decision["action"] in ["approve", "edit"]:
            insert_log("sent", state['requester'], state.get('topic', 'General'), decision["content"], decision["action"])
        else:
            insert_log("sent", state['requester'], state.get('topic', 'General'), "Message Rejected", "reject")
        
        if decision and decision["action"] == "approve":
            print("Response approved via UI.")
            graph.update_state(config, {"final_response": decision["content"]})
            for event in graph.stream(None, config):
                pass
        elif decision and decision["action"] == "edit":
            print("Response edited and approved via UI.")
            graph.update_state(config, {"final_response": decision["content"]})
            for event in graph.stream(None, config):
                pass
        else:
            print("Response rejected via UI or window closed. No message sent.")
    else:
        print("\nNo response was required for this message.")

if __name__ == "__main__":
    main()
