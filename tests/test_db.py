import pytest
from unittest.mock import patch, MagicMock
from db.core import get_db_connection, init_db
from db.logs import insert_log
from db.embeddings import get_embeddings
from langchain_core.embeddings.fake import FakeEmbeddings

@patch('db.core.psycopg.connect')
def test_get_db_connection(mock_connect):
    get_db_connection()
    mock_connect.assert_called_once()

@patch('db.core.get_db_connection')
def test_init_db(mock_get_db):
    mock_conn = MagicMock()
    mock_get_db.return_value = mock_conn
    init_db()
    # verify cursor was opened
    assert mock_conn.cursor.call_count >= 2
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called_once()

@patch('db.logs.get_db_connection')
def test_insert_log(mock_get_db):
    mock_conn = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    
    insert_log("received", "Bob", "Test Topic", "Hello World", "approve")
    
    mock_cursor.execute.assert_called_once()
    query = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO message_logs" in query
    mock_conn.commit.assert_called_once()

def test_get_embeddings_fallback(monkeypatch):
    """Test that missing API keys fallback to FakeEmbeddings."""
    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    embeddings = get_embeddings()
    assert isinstance(embeddings, FakeEmbeddings)
