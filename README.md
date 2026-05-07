# Attention Defense System (ADS)

The **Attention Defense System** is an AI-powered personal assistant designed to protect your cognitive focus by intercepting and managing incoming communications. Instead of being interrupted by every notification, ADS uses a multi-agent system to process messages, gather necessary context, and draft high-quality responses for your review.

## 🚀 Key Features

*   **Multi-Agent Architecture:** Powered by **LangGraph**, the system employs specialized "Expert Agents" (Email, Git, A2A) overseen by a Supervisor to handle complex requests.
*   **Agent-to-Agent (A2A) Discovery:** Dynamically discovers and communicates with other ADS instances via a central Registry, allowing agents to negotiate and share information autonomously.
*   **Dynamic Interaction Skills:** Automatically fetches the preferred communication style and rules for a recipient from the Registry, ensuring every message is perfectly tailored.
*   **Human-in-the-Loop:** A PyQt6-based desktop UI allows you to approve, edit, or reject drafted responses before they are sent.
*   **Unified Knowledge Base:** Ingests data from local Git repositories and Email (IMAP) into a **PGVector** document store for semantic search and retrieval.

## 🛠️ Architecture

The system is built on a modular graph-based state machine:
1.  **Supervisor:** Analyzes incoming messages and routes them to the appropriate experts.
2.  **Domain Experts:**
    *   **Git Expert:** Researches commits, PRs, and code history.
    *   **Email Expert:** Looks up past correspondence and schedule information.
    *   **A2A Expert:** Analyzes past agent-to-agent negotiations and handshakes.
3.  **Drafter:** Synthesizes expert findings and interaction preferences into a cohesive response.
4.  **Human Approval:** Blocks the workflow for final human validation via a desktop window.

## 📋 Requirements

*   Python 3.12+
*   PostgreSQL with **pgvector** extension
*   OpenAI / Anthropic / Ollama API access

## 🚦 Getting Started

### 1. Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Configuration
Copy the `.env.example` to `.env` and fill in your API keys and database connection string.

### 3. Running the Agent (Simulation)
```bash
python src/main.py
```

### 4. Running the A2A Server
To allow other agents to contact you directly:
```bash
python src/server.py
```

## 📜 Documentation
*   [Registry Specification](file:///home/ryan/.gemini/antigravity/brain/d9007b9b-c32f-4982-b983-d96268ea872c/registry_spec_sheet.md): Details on how the central discovery server works.
*   [Implementation Walkthrough](file:///home/ryan/.gemini/antigravity/brain/d9007b9b-c32f-4982-b983-d96268ea872c/walkthrough.md): Technical details on the latest feature implementations.
