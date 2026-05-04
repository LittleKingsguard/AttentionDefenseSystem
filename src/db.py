import os
import psycopg
import json
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import JinaEmbeddings
from dotenv import load_dotenv

load_dotenv()

# We use psycopg 3 async driver format, or sync driver. 
# PGVector from langchain-postgres uses sync by default if we provide postgresql+psycopg
CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql+psycopg://attention_agent:password@localhost:5444/knowledge_base")
COLLECTION_NAME = "agent_knowledge"

def get_embeddings():
    provider = os.environ.get("EMBEDDINGS_PROVIDER", "openai").lower()
    model_name = os.environ.get("EMBEDDINGS_MODEL", "text-embedding-3-small")
    
    if provider == "openai":
        if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "your_openai_api_key_here":
            return FakeEmbeddings(size=1536)
        return OpenAIEmbeddings(model=model_name)
        
    elif provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaEmbeddings(model=model_name, base_url=base_url)
        
    elif provider == "jina":
        api_key = os.environ.get("JINA_API_KEY")
        if not api_key or api_key == "your_jina_api_key_here":
            print("[WARNING] Missing JINA_API_KEY. Falling back to FakeEmbeddings.")
            return FakeEmbeddings(size=768)
        return JinaEmbeddings(jina_api_key=api_key, model_name=model_name)
        
    else:
        print(f"[WARNING] Unknown EMBEDDINGS_PROVIDER '{provider}'. Falling back to FakeEmbeddings.")
        return FakeEmbeddings(size=1536)

def get_vector_store():
    """Return the PGVector store instance."""
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING,
        use_jsonb=True,
    )

def get_db_connection():
    # Convert postgresql+psycopg to postgresql for standard psycopg connection
    conn_str = CONNECTION_STRING
    if conn_str.startswith("postgresql+psycopg://"):
        conn_str = conn_str.replace("postgresql+psycopg://", "postgresql://")
    return psycopg.connect(conn_str)

def init_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    direction VARCHAR(50),
                    party VARCHAR(255),
                    topic VARCHAR(255),
                    content TEXT,
                    action VARCHAR(50)
                )
            """)
            cur.execute("DROP TABLE IF EXISTS sync_state")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS data_connectors (
                    id VARCHAR(100) PRIMARY KEY,
                    type VARCHAR(50),
                    config JSONB,
                    last_sync_value VARCHAR(255)
                )
            """)
        conn.commit()
        
        # Auto-seed
        with conn.cursor() as cur:
            if os.environ.get("IMAP_SERVER") and os.environ.get("IMAP_USERNAME"):
                email_id = f"email_{os.environ.get('IMAP_USERNAME')}"
                cur.execute("SELECT id FROM data_connectors WHERE id = %s", (email_id,))
                if not cur.fetchone():
                    email_config = {
                        "host": os.environ.get("IMAP_SERVER"),
                        "user": os.environ.get("IMAP_USERNAME"),
                        "password": os.environ.get("IMAP_PASSWORD", ""),
                        "folder": os.environ.get("IMAP_FOLDER", "INBOX")
                    }
                    cur.execute(
                        "INSERT INTO data_connectors (id, type, config) VALUES (%s, %s, %s)",
                        (email_id, "email_imap", json.dumps(email_config))
                    )
            
            repo_path = os.environ.get("LOCAL_GIT_REPO_PATH", ".")
            if repo_path:
                abs_path = os.path.abspath(repo_path)
                git_id = f"git_{abs_path}"
                cur.execute("SELECT id FROM data_connectors WHERE id = %s", (git_id,))
                if not cur.fetchone():
                    git_config = {"repo_path": repo_path}
                    cur.execute(
                        "INSERT INTO data_connectors (id, type, config) VALUES (%s, %s, %s)",
                        (git_id, "local_git", json.dumps(git_config))
                    )
        conn.commit()
        conn.close()
        print("Database tables initialized.")
    except Exception as e:
        print(f"Error initializing DB: {e}")

def insert_log(direction, party, topic, content, action=None):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO message_logs (direction, party, topic, content, action)
                VALUES (%s, %s, %s, %s, %s)
            """, (direction, party, topic, content, action))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error inserting log: {e}")

def get_logs(limit=100, offset=0, direction=None, topic=None, party=None):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "SELECT timestamp, direction, party, topic, content, action FROM message_logs"
            conditions = []
            params = []
            
            if direction and direction != "All Directions":
                conditions.append("LOWER(direction) = LOWER(%s)")
                params.append(direction)
            if topic and topic != "All Topics":
                conditions.append("topic = %s")
                params.append(topic)
            if party and party != "All Parties":
                conditions.append("party = %s")
                params.append(party)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            # We order by timestamp DESC so the newest logs come first in pagination
            query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                "timestamp": row[0].isoformat() if row[0] else "",
                "direction": row[1],
                "party": row[2],
                "topic": row[3],
                "content": row[4],
                "action": row[5]
            })
        return logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def get_filter_options():
    try:
        conn = get_db_connection()
        topics = []
        parties = []
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT topic FROM message_logs WHERE topic IS NOT NULL")
            topics = [row[0] for row in cur.fetchall()]
            cur.execute("SELECT DISTINCT party FROM message_logs WHERE party IS NOT NULL")
            parties = [row[0] for row in cur.fetchall()]
        conn.close()
        return sorted(topics), sorted(parties)
    except Exception as e:
        print(f"Error fetching filter options: {e}")
        return [], []

def get_data_connectors():
    """Get all configured data connectors."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, type, config, last_sync_value FROM data_connectors")
            rows = cur.fetchall()
        conn.close()
        
        connectors = []
        for row in rows:
            config_val = row[2]
            if isinstance(config_val, str):
                config_val = json.loads(config_val)
                
            connectors.append({
                "id": row[0],
                "type": row[1],
                "config": config_val,
                "last_sync_value": row[3]
            })
        return connectors
    except Exception as e:
        print(f"Error getting data connectors: {e}")
        return []

def set_sync_state(connector_id: str, value: str):
    """Set the last sync state for a connector."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE data_connectors 
                SET last_sync_value = %s 
                WHERE id = %s
            """, (value, connector_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error setting sync state for {connector_id}: {e}")
