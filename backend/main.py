from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.embedding_raw_context import EmbeddingService
from src.db.index import initialize_collections
from src.db.vector_indexer import VectorIndexer
from src.utils.config import settings
from src.webhook.github_webhook import router as webhook_router

embedding_service = None
vector_indexer = None


@asynccontextmanager
async def init(app: FastAPI):
    global embedding_service, vector_indexer
    print("Initializing VectorDB")
    initialize_collections()
    print("Loading embedding model")
    embedding_service = EmbeddingService()
    print("Loading vector indexer")
    vector_indexer = VectorIndexer(embedding_service)
    app.state.embedding_service = embedding_service
    app.state.vector_indexer = vector_indexer
    print("Successfully initiated")
    yield


app = FastAPI(title="CodeRabbit Test", lifespan=init)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://codeboss-one.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/api")

if __name__ == "__main__":
    port = int(getattr(settings, "port", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
