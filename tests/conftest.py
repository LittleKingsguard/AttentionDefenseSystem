import sys
import os
import pytest

# Add src to Python path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Ensure tests run with predictable environment variables."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test_db")
    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "openai")
