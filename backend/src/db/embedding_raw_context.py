from typing import Any, Dict, List
import asyncio
import concurrent.futures
from utils.ai_client import AIClient
# from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):
        self.ai_client = AIClient(provider="gemini")
        self.embedding_dim = 768
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        print(f"Gemini Embeddings loaded: {self.embedding_dim}")

    def embed_text(self, text: str):
        if not text or not text.strip():
            return [0.0] * self.embedding_dim
        future = self._executor.submit(self._embed_sync, text)
        return future.result()
    
    def _embed_sync(self, text: str):
        return asyncio.run(self.ai_client.generate_embedding(text))

    def embed_batch(self, texts: List[str]):
        valid_texts = [t if t and t.strip() else " " for t in texts]
        
        future = self._executor.submit(self._embed_batch_sync, valid_texts)
        return future.result()
    
    def _embed_batch_sync(self, texts: List[str]):
        async def batch_embed():
            tasks = [self.ai_client.generate_embedding(t) for t in texts]
            return await asyncio.gather(*tasks)
        return asyncio.run(batch_embed())

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