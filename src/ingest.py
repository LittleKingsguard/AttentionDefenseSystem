from db import get_vector_store, get_data_connectors, set_sync_state, init_db
from langchain_core.documents import Document

from connectors.email_connector import EmailConnector
from connectors.git_connector import GitConnector

from typing import Optional

def sync_connectors(target_connector_id: Optional[str] = None):
    # Ensure DB tables exist
    init_db()
    
    print("Connecting to vector store...")
    vector_store = get_vector_store()
    
    db_connectors = get_data_connectors()
    
    connectors = []
    for dc in db_connectors:
        if target_connector_id and dc["id"] != target_connector_id:
            continue
            
        if dc["type"] == "email_imap":
            connectors.append((EmailConnector(dc["id"], dc["config"]), dc["last_sync_value"]))
        elif dc["type"] == "local_git":
            connectors.append((GitConnector(dc["id"], dc["config"]), dc["last_sync_value"]))
        else:
            print(f"Unknown connector type: {dc['type']}")
    
    all_docs = []
    for connector, state in connectors:
        print(f"Fetching updates from {connector.connector_id} (last sync state: {state})...")
        
        docs, new_state = connector.fetch_updates(state)
        if docs:
            print(f"Found {len(docs)} new documents from {connector.connector_id}.")
            all_docs.extend(docs)
            
            # Update state immediately for this connector
            if new_state:
                set_sync_state(connector.connector_id, new_state)
            
    if all_docs:
        print(f"Ingesting {len(all_docs)} total documents into PGVector...")
        vector_store.add_documents(all_docs)
        print("Ingestion complete! Run the agent to query this knowledge.")
    else:
        print("No new documents found across all connectors.")

if __name__ == "__main__":
    sync_connectors()
