from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded: {self.embedding_dim}")

    def embed_text(self, text: str):
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]):
        valid_texts = [t if t and t.strip() else " " for t in texts]
        embeddings = self.model.encode(
            valid_texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_code_graph(self, graph_data: Dict[str, Any]):
        content = f"""
        File: {graph_data.get('file_path', '')}
        Functions: {', '.join(graph_data.get('functions', []))}
        Classes: {', '.join(graph_data.get('classes', []))}
        Function Calls: {', '.join(graph_data.get('calls', []))}
        Total Nodes: {graph_data.get('nodes', 0)}
        Total Edges: {graph_data.get('edges', 0)}
        """
        return self.embed_text(content.strip())

    def embed_import_file(self, file_path: str, source_code: str, imports: List[str]):
        content = f"""
        File: {file_path}
        Imports: {', '.join(imports)}
        Source Code: {source_code}
        """
        return self.embed_text(content.strip())

    def embed_learning(
        self,
        commit_message: str,
        bot_comment: str,
        user_feedback: str = "",
        code_context: str = "",
    ):
        content = f"""
        Commit: {commit_message}
        Bot Review: {bot_comment}
        User Feedback: {user_feedback if user_feedback else "No feedback yet"}
        Code Context: {code_context[:500] if code_context else "Nothing yet"}
        """
        return self.embed_text(content.strip())
