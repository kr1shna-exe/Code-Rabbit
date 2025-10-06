import google.generativeai as genai
from utils.config import settings
genai.configure(api_key=settings.gemini_api_key)

def review_code(diff: str, pr_title: str, context: str):
    prompt = f"""You are CodeRabbit, an expert AI code reviewer with deep codebase knowledge.

**Pull Request: {pr_title}**

{context}

**Code Changes:**
{diff}

**Review Guidelines:**
1. Analyze changes considering complexity, dependencies, and cross-file impact
2. Check if modified functions will break their callers
3. Compare against similar patterns in the codebase
4. Flag potential bugs, security issues, and performance problems
5. Suggest specific improvements with code examples
6. Verify import/dependency changes are safe

**Format your response with these sections:**

## 🔴 Potential Issues Found
- Critical bugs and errors that must be fixed
- Security vulnerabilities
- Breaking changes
- Performance bottlenecks

## 🛠️ Fixes
- Specific code fixes for identified issues
- Refactoring suggestions
- Best practice implementations

## 🔒 Security Implications
- Security concerns and vulnerabilities
- Input validation issues
- Authentication/authorization problems
- Data exposure risks

## ✅ Positive Aspects
- Good practices and patterns
- Well-implemented features
- Clean code examples

Be specific, actionable, and reference line numbers where applicable.
"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    return response.text