import os
import psycopg
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings.fake import FakeEmbeddings
from dotenv import load_dotenv

load_dotenv()

# We use psycopg 3 async driver format, or sync driver. 
# PGVector from langchain-postgres uses sync by default if we provide postgresql+psycopg
CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql+psycopg://attention_agent:password@localhost:5444/knowledge_base")
COLLECTION_NAME = "agent_knowledge"

def get_embeddings():
    if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") == "your_openai_api_key_here":
        # Returns fake 1536-dimensional embeddings (same dimension as OpenAI)
        return FakeEmbeddings(size=1536)
    return OpenAIEmbeddings(model="text-embedding-3-small")

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
