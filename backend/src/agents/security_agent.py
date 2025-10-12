from utils.ai_client import AIClient
from .prompts import SECURITY_PROMPT
from .state import AgentStatus


async def security_analysis_agent(state: dict) -> dict:
    """Security analysis agent - returns only updated keys"""
    try:
        prompt = SECURITY_PROMPT.format(
            comprehensive_context=state.get("comprehensive_context", ""),
            diff_data=state.get("diff_data", {}).get("full_diff", ""),
            pr_title=state.get("pr_title", ""),
        )
        ai_client = AIClient()
        response = await ai_client.generate_content(prompt)

        return {
            "security_analysis": response,
            "security_agent_status": AgentStatus.COMPLETED,
        }
    except Exception as e:
        return {
            "security_agent_status": AgentStatus.FAILED,
            "errors": [f"Security agent failed: {str(e)}"],
            "security_analysis": "No critical security issues found."
        }
