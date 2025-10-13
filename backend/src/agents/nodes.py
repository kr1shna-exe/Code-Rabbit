from db.embedding_raw_context import EmbeddingService
from db.vector_indexer import VectorIndexer

embedding_service = EmbeddingService()
vector_indexer = VectorIndexer(embedding_service)


def search_vector_tool(query: str, limit: int = 10):
    graph_results = vector_indexer._search_similar_graphs(query, limit)
    raw_graph_context = []
    raw_source_code_context = []
    if graph_results:
        for item in graph_results:
            raw_graph_context.append(
                {
                    "ref_id": item.payload.get("file_path", ""),
                    "context": f"Functions: {item.payload.get('functions', [])}, Classes: {item.payload.get('classes', [])}",
                    "score": item.score,
                }
            )
    file_results = vector_indexer._search_similar_files(query, limit)
    if file_results:
        for item in file_results:
            raw_source_code_context.append(
                {
                    "ref_id": item.payload.get("file_path", ""),
                    "context": item.payload.get("source_code", ""),
                    "score": item.score,
                }
            )
    return {
        "raw_graph_context": raw_graph_context,
        "raw_source_code_context": raw_source_code_context,
    }


def search_learning_tool(query: str, limit: int = 10):
    results = vector_indexer._search_similar_learnings(query, limit)
    if not results:
        return ""
    learnings_summary = "\n".join(
        [
            f"- {hit.payload.get('commit_message', '')}: {hit.payload.get('bot_comment', '')}"
            for hit in results
        ]
    )
    return learnings_summary
