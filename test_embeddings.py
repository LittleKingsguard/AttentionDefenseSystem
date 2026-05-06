import os
from dotenv import load_dotenv
load_dotenv('.env.example')
from src.db.embeddings import get_vector_store
vs = get_vector_store()
try:
    print(vs.similarity_search("test", k=1))
except Exception as e:
    print("ERROR:", e)
