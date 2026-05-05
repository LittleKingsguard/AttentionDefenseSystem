import json
from .core import get_db_connection

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

def upsert_data_connector(connector_id: str, c_type: str, config: dict):
    """Insert or update a data connector configuration."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO data_connectors (id, type, config)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET type = EXCLUDED.type, config = EXCLUDED.config
            """, (connector_id, c_type, json.dumps(config)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error upserting data connector: {e}")
        return False

def delete_data_connector(connector_id: str):
    """Delete a data connector configuration."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM data_connectors WHERE id = %s", (connector_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting data connector: {e}")
        return False
