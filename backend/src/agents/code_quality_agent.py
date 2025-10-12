from utils.ai_client import AIClient
from .prompts import CODE_QUALITY_PROMPT
from .state import AgentStatus


async def code_quality_analysis_agent(state: dict) -> dict:
    """Code quality analysis agent - returns only updated keys"""
    try:
        prompt = CODE_QUALITY_PROMPT.format(
            comprehensive_context=state.get("comprehensive_context", ""),
            diff_data=state.get("diff_data", {}).get("full_diff", ""),
            pr_title=state.get("pr_title", ""),
        )
        ai_client = AIClient()
        response = await ai_client.generate_content(prompt)

        return {
            "code_quality_analysis": response,
            "code_quality_agent_status": AgentStatus.COMPLETED,
        }
    except Exception as e:
        return {
            "code_quality_agent_status": AgentStatus.FAILED,
            "errors": [f"Code quality agent failed: {str(e)}"],
            "code_quality_analysis": f"Code quality analysis failed: {str(e)}"
        }
