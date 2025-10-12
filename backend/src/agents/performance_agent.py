from utils.ai_client import AIClient
from .prompts import PERFORMANCE_PROMPT
from .state import AgentStatus


async def performance_analysis_agent(state: dict) -> dict:
    """Performance analysis agent - returns only updated keys"""
    try:
        prompt = PERFORMANCE_PROMPT.format(
            comprehensive_context=state.get("comprehensive_context", ""),
            diff_data=state.get("diff_data", {}).get("full_diff", ""),
            pr_title=state.get("pr_title", ""),
        )
        ai_client = AIClient()
        response = await ai_client.generate_content(prompt)

        return {
            "performance_analysis": response,
            "performance_agent_status": AgentStatus.COMPLETED,
        }
    except Exception as e:
        return {
            "performance_agent_status": AgentStatus.FAILED,
            "errors": [f"Performance agent failed: {str(e)}"],
            "performance_analysis": f"Performance analysis failed: {str(e)}"
        }
