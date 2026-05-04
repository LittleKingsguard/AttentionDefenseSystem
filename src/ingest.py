from db import get_vector_store
from langchain_core.documents import Document

def ingest_mock_data():
    print("Connecting to vector store...")
    vector_store = get_vector_store()
    
    # Simulate data coming from a Jira connector and a Git connector
    mock_documents = [
        Document(
            page_content="Ticket-404: Root cause identified as null pointer in auth module. Fix deployed to staging, awaiting QA signoff. (Jira update by Alice)",
            metadata={"source": "jira", "ticket_id": "Ticket-404"}
        ),
        Document(
            page_content="Ticket-405: The UI is completely broken on Safari. Investigating CSS grid issues. (Jira update by Bob)",
            metadata={"source": "jira", "ticket_id": "Ticket-405"}
        ),
        Document(
            page_content="Commit abc1234: Fixed null pointer exception in AuthController.java by adding null check before accessing token. (Git commit by Alice)",
            metadata={"source": "git", "commit_hash": "abc1234"}
        ),
        Document(
            page_content="Slack message from Charlie: 'Hey guys, when is the staging deployment happening for the auth fix?' Alice replied: 'It is deployed right now, waiting for QA.'",
            metadata={"source": "slack", "channel": "dev-ops"}
        ),
        Document(
            page_content="Email from Dave (Support): 'Customer reported Ticket-404 still occurring for them. Can we get a status update?'",
            metadata={"source": "email", "sender": "Dave"}
        )
    ]
    
    print("Ingesting mock documents into PGVector...")
    # Add documents to the vector store
    vector_store.add_documents(mock_documents)
    print("Ingestion complete! Run the agent to query this knowledge.")

if __name__ == "__main__":
    ingest_mock_data()
