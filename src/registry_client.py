import os
import requests
from typing import Optional
from datetime import datetime, timedelta

# Simple in-memory cache
# Format: { "user_id": {"record": dict, "expires_at": datetime} }
_cache = {}

REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000/api/v1/registry")

def _get_user_record(user_id: str) -> dict:
    """
    Internal helper to fetch and cache the full user record from the registry.
    """
    now = datetime.now()
    
    # Check cache
    if user_id in _cache:
        cache_entry = _cache[user_id]
        if now < cache_entry["expires_at"]:
            return cache_entry["record"]
            
    # Fetch from registry
    try:
        url = f"{REGISTRY_URL}/{user_id}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            record = response.json()
            
            # Cache the result for 24 hours
            _cache[user_id] = {
                "record": record,
                "expires_at": now + timedelta(hours=24)
            }
            return record
            
    except requests.RequestException as e:
        print(f"[RegistryClient] Error fetching record for {user_id}: {e}")
        
    return {}

def get_interaction_skills(user_id: str) -> Optional[dict]:
    """
    Fetches the interaction skills for a given user from the central registry.
    Returns the skills dictionary, or None if not found.
    """
    record = _get_user_record(user_id)
    return record.get("interaction_skills")

def get_agent_address(user_id: str) -> Optional[str]:
    """
    Fetches the network address (URL) for a given agent from the registry.
    Useful for outbound A2A communication.
    """
    record = _get_user_record(user_id)
    return record.get("address")

def register_agent(user_id: str, address: str, interaction_skills: Optional[dict] = None):
    """
    Registers the current agent in the central registry.
    """
    payload = {
        "user_id": user_id,
        "address": address,
        "interaction_skills": interaction_skills or {
            "relationship_type": "standard",
            "tone_preference": "professional",
            "rules": [],
            "permissions": {}
        }
    }
    try:
        # Note: The registry expects POST /api/v1/registry/
        # REGISTRY_URL is already defined as .../api/v1/registry
        url = f"{REGISTRY_URL}/"
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            print(f"[RegistryClient] Successfully registered agent for {user_id} at {address}")
            return True
        else:
            print(f"[RegistryClient] Registration failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[RegistryClient] Error during registration: {e}")
    return False
