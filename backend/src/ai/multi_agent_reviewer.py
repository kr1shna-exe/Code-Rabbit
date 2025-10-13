from typing import Any, Dict

from agents.graph import create_code_review_agent
from agents.state import AgentStatus, CodeReviewState


async def review_code_with_multi_agents(diff: str, pr_title: str, context: str, pr_data: Dict[str, Any], diff_data: Dict[str, Any]):
    agent_graph = create_code_review_agent()
    initial_state = CodeReviewState(
        pr_data=pr_data or {},
        diff_data=diff_data or {"full_diff": diff},
        changed_files=diff_data.get("diff_files", []) if diff_data else [],
        pr_title=pr_title,
        pr_description=pr_data.get("body", "") if pr_data else "",
        vector_context={},
        code_graphs=[],
        import_files=[],
        learnings=[],
        comprehensive_context=context,
        context_fetcher_status=AgentStatus.PENDING,
        security_agent_status=AgentStatus.PENDING,
        code_quality_agent_status=AgentStatus.PENDING,
        performance_agent_status=AgentStatus.PENDING,
        aggregator_status=AgentStatus.PENDING,
        security_analysis="",
        code_quality_analysis="",
        performance_analysis="",
        final_review="",
        inline_comments=[],
        total_issues=0,
        errors=[],
        warnings=[]
    )
    try:
        result = await agent_graph.ainvoke(initial_state)

        return {
            "summary": result.get("final_review", "Review generation failed"),
            "inline_comments": result.get("inline_comments", []),
            "total_issues": result.get("total_issues", 0)
        }

    except Exception as e:
        return {
            "summary": f"Multi-agent review failed: {str(e)}",
            "inline_comments": [],
            "total_issues": 0
        }