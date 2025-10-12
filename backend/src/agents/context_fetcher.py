import asyncio

from services.vector_retriever import VectorRetriever

from .state import AgentStatus


async def context_fetcher_agent(state: dict) -> dict:
    """Context fetcher agent - returns only updated keys"""
    try:
        changed_files = state.get("changed_files", [])
        vector_retriever = VectorRetriever()

        code_graphs = await asyncio.to_thread(vector_retriever.get_code_graphs_by_files, changed_files)
        import_files = await asyncio.to_thread(vector_retriever.get_import_files_by_files, changed_files)
        learnings = await asyncio.to_thread(vector_retriever.get_related_learnings, limit=5)

        comprehensive_context = vector_retriever.format_for_ai(
            code_graphs, import_files, learnings
        )

        return {
            "vector_context": {
                "code_graphs": code_graphs,
                "import_files": import_files,
                "learnings": learnings,
            },
            "code_graphs": code_graphs,
            "import_files": import_files,
            "learnings": learnings,
            "comprehensive_context": comprehensive_context,
            "context_fetcher_status": AgentStatus.COMPLETED,
        }
    except Exception as e:
        return {
            "context_fetcher_status": AgentStatus.FAILED,
            "errors": [f"Context fetcher failed: {str(e)}"]
        }
