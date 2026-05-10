import os
import requests

RADAR_URL = os.environ.get("RADAR_URL", "http://localhost:8002")

def subscribe_to_topic(user_id: str, topic_name: str, is_subscribed: bool = True):
    """
    Subscribe or unsubscribe the user to a specific topic in the Radar service.
    """
    url = f"{RADAR_URL}/api/v1/radar/subscribe"
    payload = {
        "user_id": user_id,
        "topic_name": topic_name,
        "is_subscribed": is_subscribed
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[RadarClient] Error subscribing to topic: {e}")
        return None
