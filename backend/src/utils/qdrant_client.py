import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()
URL = os.getenv("QDRANT_DB")
API_KEY = os.getenv("QDRANT_API_KEY")

qdrant_client = QdrantClient(url=URL, api_key=API_KEY)
