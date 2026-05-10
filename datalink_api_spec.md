# Datalink Service - API Specification

This document defines the interface for the **Datalink RAG Service**. ADS agents use this service to perform semantic searches and push updates from disparate communication channels.

## 1. API Overview

*   **Base URL:** `http://localhost:8001` (Default)
*   **Protocol:** HTTP/JSON
*   **Auth:** None (Internal Network)

## 2. Endpoints

### 2.1 Semantic Search
Retrieve the most relevant message fragments based on a natural language query.

*   **Endpoint:** `POST /query`
*   **Content-Type:** `application/json`
*   **Request Schema (`MessageQuery`):**
    ```json
    {
      "query": "string (Required, search terms)",
      "top_k": "integer (Optional, default: 5)",
      "platform": "string (Optional, 'slack', 'teams', 'email', 'a2a')"
    }
    ```

### 2.2 Data Ingestion
Push new messages/updates into the document store. This automatically triggers embedding and topic extraction via Radar.

*   **Endpoint:** `POST /ingest`
*   **Content-Type:** `application/json`
*   **Request Schema (`MessageIngest`):**
    ```json
    {
      "platform": "string (Required, e.g., 'email', 'a2a')",
      "channel_id": "string (Required, unique ID for the thread/context)",
      "user_id": "string (Required, the message author)",
      "content": "string (Required, the message text)"
    }
    ```

## 3. Implementation Notes for ADS Platform

*   **Vector Search:** Queries are embedded using Ollama and compared using cosine similarity.
*   **Context Injection:** Agents should concatenate the `content` of returned messages into their prompt context.
*   **Radar Integration:** Every message pushed via `/ingest` is asynchronously forwarded to the **Radar** service for keyword extraction and topic tracking.
