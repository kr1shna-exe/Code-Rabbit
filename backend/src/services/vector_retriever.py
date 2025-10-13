from typing import Dict, List

from src.utils.qdrant_client import qdrant_client


class VectorRetriever:
    """Simple VectorDB retriever for getting stored code data"""

    def __init__(self):
        pass

    def get_code_graphs_by_files(self, file_paths: List[str]) -> List[Dict]:
        results = []

        for file_path in file_paths:
            try:
                # Search for exact file matches
                search_result = qdrant_client.scroll(
                    collection_name="code_graphs",
                    scroll_filter={
                        "must": [{"key": "file_path", "match": {"value": file_path}}]
                    },
                    limit=1,  # Get latest version
                    with_payload=True,
                )[0]

                if search_result:
                    results.append(search_result[0].payload)

            except Exception as e:
                print(f"Error getting code graph for {file_path}: {e}")

        return results

    def get_import_files_by_files(self, file_paths: List[str]) -> List[Dict]:
        """Get import files (source code) for specific file paths"""
        results = []

        for file_path in file_paths:
            try:
                search_result = qdrant_client.scroll(
                    collection_name="import_files",
                    scroll_filter={
                        "must": [{"key": "file_path", "match": {"value": file_path}}]
                    },
                    limit=1,
                    with_payload=True,
                )[0]

                if search_result:
                    results.append(search_result[0].payload)

            except Exception as e:
                print(f"Error getting import file for {file_path}: {e}")

        return results

    def get_related_learnings(self, limit: int = 3) -> List[Dict]:
        """Get recent learnings (past commits, comments, feedback)"""
        try:
            # Get most recent learnings (no ordering)
            result = qdrant_client.scroll(
                collection_name="learnings", limit=limit, with_payload=True
            )[0]

            return [item.payload for item in result]

        except Exception as e:
            print(f"Error getting learnings: {e}")
            return []

    def format_for_ai(
        self, code_graphs: List[Dict], import_files: List[Dict], learnings: List[Dict]
    ) -> str:
        """Format retrieved data for AI consumption"""
        context_parts = []

        # Add learnings first (most important)
        if learnings:
            context_parts.append("## Past Learnings:")
            for learning in learnings:
                context_parts.append(f"- {learning.get('commit_message', 'N/A')}")
                context_parts.append(
                    f"  Bot: {learning.get('bot_comment', 'N/A')[:100]}..."
                )
                if learning.get("user_feedback"):
                    context_parts.append(
                        f"  User: {learning.get('user_feedback', 'N/A')[:100]}..."
                    )

        # Add code graphs
        if code_graphs:
            context_parts.append("\n## Code Structure:")
            for graph in code_graphs:
                context_parts.append(f"- {graph.get('file_path', 'N/A')}")
                context_parts.append(
                    f"  Functions: {', '.join(graph.get('functions', []))}"
                )
                context_parts.append(
                    f"  Classes: {', '.join(graph.get('classes', []))}"
                )

        # Add source code
        if import_files:
            context_parts.append("\n## Source Code:")
            for file_data in import_files:
                context_parts.append(f"- {file_data.get('file_path', 'N/A')}")
                source_preview = file_data.get("source_code", "")[:200]
                context_parts.append(f"  ```python\n{source_preview}...\n```")

        return "\n".join(context_parts)

