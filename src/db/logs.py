from .core import get_db_connection

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
