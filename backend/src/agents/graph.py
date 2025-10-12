from langgraph.graph import END, START, StateGraph

from .aggregator import aggregator_agent
from .code_quality_agent import code_quality_analysis_agent
from .context_fetcher import context_fetcher_agent
from .performance_agent import performance_analysis_agent
from .security_agent import security_analysis_agent
from .state import CodeReviewState


def create_code_review_agent() -> StateGraph:
    """
    Creating a multi-agent code review workflow with parallel execution.
    """
    workflow = StateGraph(CodeReviewState)

    # Add all nodes
    workflow.add_node("context_fetcher", context_fetcher_agent)
    workflow.add_node("security_analysis", security_analysis_agent)
    workflow.add_node("code_quality_analysis", code_quality_analysis_agent)
    workflow.add_node("performance_analysis", performance_analysis_agent)
    workflow.add_node("aggregator", aggregator_agent)

    # Entry point
    workflow.add_edge(START, "context_fetcher")

    # Fan out: context_fetcher → all 3 analysis agents (parallel)
    workflow.add_edge("context_fetcher", "security_analysis")
    workflow.add_edge("context_fetcher", "code_quality_analysis")
    workflow.add_edge("context_fetcher", "performance_analysis")

    # Fan in: all 3 agents → aggregator (LangGraph waits for all)
    workflow.add_edge("security_analysis", "aggregator")
    workflow.add_edge("code_quality_analysis", "aggregator")
    workflow.add_edge("performance_analysis", "aggregator")

    # End
    workflow.add_edge("aggregator", END)

    return workflow.compile()
