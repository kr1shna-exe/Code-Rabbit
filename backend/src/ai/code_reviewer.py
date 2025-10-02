import google.generativeai as genai
from src.utils.config import settings
from src.services.ast_parser import ASTAnalyzer
genai.configure(api_key=settings.gemini_api_key)

def review_code(diff: str, pr_title: str, files_changed: list):
    prompt = f"""You are an expert code reviewer.Review this pull request and provide feedback.
**Pull Request: {pr_title}**
**Files Changed: {', '.join(files_changed)}**
**Code Changes: {diff}**
Please provide:
1. Summary of changes
2. Any bugs or issues you find
3. Code quality suggestions
4. Security concerns (if any)
5. Overall assessment

Keep it clear and actionable."""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    return response.text