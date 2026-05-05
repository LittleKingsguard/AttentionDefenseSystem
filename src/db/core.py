import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv('.env.example')

CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql+psycopg://attention_agent:password@localhost:5444/knowledge_base")

def get_db_connection():
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
