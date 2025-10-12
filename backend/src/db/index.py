from qdrant_client.models import Distance, VectorParams

from utils.qdrant_client import qdrant_client

VECTOR_SIZE = 384
COLLECTIONS = {
    "code_graphs": {
        "description": "Code structure graphs with functions, classes and calls",
        "vector_size": VECTOR_SIZE,
    },
    "import_files": {
        "description": "Source code files with their import dependiencies",
        "vector_size": VECTOR_SIZE,
    },
    "learnings": {
        "description": "Learnings from the pr commints & comments along with user feedback",
        "vector_size": VECTOR_SIZE,
    },
}


def initialize_collections():
    existing_collections = [c.name for c in qdrant_client.get_collections().collections]
    for collection_name, config in COLLECTIONS.items():
        if collection_name not in existing_collections:
            print(f"Creating Qdrant collection: {collection_name}")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config["vector_size"], distance=Distance.COSINE
                ),
                shard_number=6,
                replication_factor=2,
            )
        else:
            print(f"Collection: {collection_name} already exists")


if __name__ != "__main__":
    initialize_collections()
