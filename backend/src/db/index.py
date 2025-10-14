from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from utils.qdrant_client import qdrant_client

VECTOR_SIZE = 768
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

        # Create payload indexes for filtering
        try:
            if collection_name in ["code_graphs", "import_files"]:
                qdrant_client.create_payload_index(
                    collection_name=collection_name,
                    field_name="file_path",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                print(f"Created payload index for {collection_name}.file_path")
        except Exception as e:
            # Index might already exist
            if "already exists" not in str(e).lower():
                print(f"Note: Could not create index for {collection_name}.file_path: {e}")


if __name__ != "__main__":
    initialize_collections()
