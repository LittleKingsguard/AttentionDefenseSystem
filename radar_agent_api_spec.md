# ADS Agent - Radar Integration API Specification

This document defines the interface that ADS agents must implement to interact with the **Radar** topic tracking service.

## 1. Outbound: Subscribing to Topics
Agents should allow users to subscribe to topics discovered by Radar.

*   **Radar Endpoint:** `POST /api/v1/radar/subscribe`
*   **Request Body:**
    ```json
    {
      "user_id": "user@example.com",
      "topic_name": "Project Apollo",
      "is_subscribed": true
    }
    ```

## 2. Inbound: Receiving Notifications
Agents MUST implement an endpoint to receive alerts from Radar when a tracked topic is mentioned.

*   **Endpoint:** `POST /api/v1/notify`
*   **Expected Payload:**
    ```json
    {
      "topic": "Project Apollo",
      "category": "Project",
      "action": "query_datalink",
      "message": "New activity detected on topic: Project Apollo"
    }
    ```
*   **Expected Agent Behavior:**
    *   Parse the topic and category.
    *   Trigger an internal search via the **Datalink** service (`POST /query`) to gather recent context about the topic.
    *   Update the agent's internal state or notify the human user if appropriate.

## 3. Interaction Flow
1.  **Datalink** ingest a message -> Sends content to **Radar**.
2.  **Radar** extracts "Project Alpha".
3.  **Radar** identifies that "user_b" is subscribed to "Project Alpha".
4.  **Radar** lookups "user_b" address in **Registry**.
5.  **Radar** sends `POST /api/v1/notify` to **user_b's Agent**.
6.  **Agent** queries **Datalink** for "Project Alpha" updates.
