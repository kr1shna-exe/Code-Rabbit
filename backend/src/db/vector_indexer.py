import uuid
from typing import Any, Dict, List

import networkx as nx
from qdrant_client.models import PointStruct

from utils.qdrant_client import qdrant_client


class VectorIndexer:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service

    def index_code_graph(self, file_path: str, graph: nx.DiGraph):
        functions = [
            data["name"]
            for node, data in graph.nodes(data=True)
            if data.get("type") == "function"
        ]
        classes = [
            data["name"]
            for node, data in graph.nodes(data=True)
            if data.get("type") == "class"
        ]
        calls = [
            data["name"]
            for node, data in graph.nodes(data=True)
            if data.get("type") == "call"
        ]
        graph_data = {
            "file_path": file_path,
            "functions": functions,
            "classes": classes,
            "calls": calls,
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
        }
        embedding = self.embedding_service.embed_code_graph(graph_data)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "code_graph",
                "file_path": file_path,
                "functions": functions,
                "classes": classes,
                "calls": calls,
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
            },
        )
        qdrant_client.upsert(collection_name="code_graphs", points=[point])
        return point.id

    def index_import_file(
        self,
        file_path: str,
        source_code: str,
        imports: List[str],
    ):
        embedding = self.embedding_service.embed_import_file(
            file_path, source_code, imports
        )
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "import_file",
                "file_path": file_path,
                "source_code": source_code,
                "imports": imports,
                "import_count": len(imports),
            },
        )
        qdrant_client.upsert(collection_name="import_files", points=[point])
        return point.id

    def index_learning(
        self,
        commit: Dict[str, Any],
        bot_comment: Dict[str, Any],
        user_feedback: Dict[str, Any] | None = None,
        code_context: str = "",
    ):
        embedding = self.embedding_service.embed_learning(
            commit_message=commit.get("message", ""),
            bot_comment=bot_comment.get("comment", ""),
            user_feedback=user_feedback.get("comment", "") if user_feedback else "",
            code_context=code_context,
        )
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "type": "learning",
                "commit_sha": commit.get("sha", ""),
                "commit_message": commit.get("message", ""),
                "bot_comment": bot_comment.get("comment", ""),
                "bot_comment_file": bot_comment.get("file", ""),
                "user_feedback": (
                    user_feedback.get("comment", "") if user_feedback else None
                ),
                "user_feedback_author": (
                    user_feedback.get("author", "") if user_feedback else None
                ),
                "has_user_feedback": user_feedback is not None,
                "code_context": code_context[:1000] if code_context else "",
            },
        )
        qdrant_client.upsert(collection_name="learnings", points=[point])
        return point.id

    def _search_similar_graphs(self, query: str, limit: int = 10):
        query_vector = self.embedding_service.embed_text(query)
        results = qdrant_client.search(
            collection_name="code_graphs", query_vector=query_vector, limit=limit
        )
        return results

    def _search_similar_files(self, query: str, limit: int = 10):
        query_vector = self.embedding_service.embed_text(query)
        results = qdrant_client.search(
            collection_name="import_files", query_vector=query_vector, limit=limit
        )
        return results

    def _search_similar_learnings(self, query: str, limit: int = 10):
        query_vector = self.embedding_service.embed_text(query)
        results = qdrant_client.search(
            collection_name="learnings", query_vector=query_vector, limit=limit
        )
        return results
