import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, TypedDict


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    return {**dict1, **dict2}


class AgentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeReviewState(TypedDict):
    pr_data: Annotated[Dict[str, Any], merge_dicts]
    diff_data: Annotated[Dict[str, Any], merge_dicts]
    changed_files: Annotated[List[str], operator.add]
    pr_title: Annotated[str, lambda a, b: b]
    pr_description: Annotated[str, lambda a, b: b]

    vector_context: Annotated[Dict[str, Any], merge_dicts]
    code_graphs: Annotated[List[Dict], operator.add]
    import_files: Annotated[List[Dict], operator.add]
    learnings: Annotated[List[Dict], operator.add]
    comprehensive_context: Annotated[str, lambda a, b: b]

    context_fetcher_status: Annotated[AgentStatus, lambda a, b: b]
    security_agent_status: Annotated[AgentStatus, lambda a, b: b]
    code_quality_agent_status: Annotated[AgentStatus, lambda a, b: b]
    performance_agent_status: Annotated[AgentStatus, lambda a, b: b]
    aggregator_status: Annotated[AgentStatus, lambda a, b: b]

    security_analysis: Annotated[str, lambda a, b: b]
    code_quality_analysis: Annotated[str, lambda a, b: b]
    performance_analysis: Annotated[str, lambda a, b: b]

    final_review: Annotated[str, lambda a, b: b]
    inline_comments: Annotated[List[Dict], operator.add]
    total_issues: Annotated[int, lambda a, b: b]

    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]
