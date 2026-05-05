import os
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import JinaEmbeddings
from .core import CONNECTION_STRING

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
