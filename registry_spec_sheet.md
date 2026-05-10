# Registry Webserver Specification

This document defines the technical requirements and expected behavior for the **Attention Defense System (ADS) Discovery Registry**. This server acts as the central directory that enables distributed ADS instances to discover each other and retrieve interaction preferences.

## 1. API Overview

*   **Base URL Path:** `/api/v1/registry`
*   **Protocol:** HTTPS (Production) / HTTP (Local Development)
*   **Content Type:** `application/json`

---

## 2. Endpoints

### 2.1 Register/Update User
Used by an ADS instance to broadcast its presence and capabilities.

*   **Endpoint:** `POST /`
*   **Request Body Schema:**
    ```json
    {
      "user_id": "string (Required, unique email or handle)",
      "address": "string (Required, URL of the agent node)",
      "public_key": "string (Optional, RSA/Ed25519 public key)",
      "protocols": "array of strings (Optional, e.g., ['ads-v1'])",
      "interaction_skills": {
        "relationship_type": "string",
        "tone_preference": "string",
        "rules": "array of strings",
        "permissions": "object"
      }
    }
    ```
*   **Expected Behavior:**
    *   If `user_id` does not exist: Create a new record.
    *   If `user_id` exists: Overwrite the existing record with the new data (Update).
    *   Return `201 Created` for new records or `200 OK` for updates.

### 2.2 Lookup User
Used by an ADS instance to find a recipient and determine how to communicate with them.

*   **Endpoint:** `GET /{user_id}`
*   **Response Body Schema:**
    ```json
    {
      "user_id": "string",
      "address": "string",
      "public_key": "string",
      "protocols": ["string"],
      "interaction_skills": {
        "relationship_type": "string",
        "tone_preference": "string",
        "rules": ["string"],
        "permissions": {}
      }
    }
    ```
*   **Expected Behavior:**
    *   If `user_id` found: Return `200 OK` with the full user record.
    *   If `user_id` NOT found: Return `404 Not Found`.

---

## 3. Storage & Lifecycle

*   **Persistence:** The server MUST persist user records in a relational or document database.
*   **Discovery TTL:** ADS instances are expected to re-register periodically. The registry MAY implement an expiration/heartbeat mechanism where records are purged if not updated within a certain timeframe (e.g., 30 days).

---

## 4. Security Considerations (Future)

*   **Authentication:** Registration SHOULD eventually require a token or signature to prevent unauthorized users from overwriting another person's agent address.
*   **Encryption:** The `public_key` field is critical for enabling encrypted handshakes between nodes. The registry MUST treat this as a public field.

---

## 5. Client Implementation Reference

The ADS application implements this contract in `src/registry_client.py`. 
*   It performs a `GET` request to `{REGISTRY_URL}/{user_id}`.
*   It specifically extracts the `interaction_skills` key for prompt injection.
*   It specifically extracts the `address` key for outbound A2A handshakes.
