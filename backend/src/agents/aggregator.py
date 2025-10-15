import re
from typing import Dict, List, Optional

from .state import AgentStatus


class ParsedIssue:
    def __init__(
        self,
        file_path: str,
        line: int,
        severity: str,
        description: str,
        current_code: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.file_path = file_path
        self.line = line
        self.severity = severity
        self.description = description
        self.current_code = current_code
        self.suggestion = suggestion


def parse_agent_issues(
    agent_output: str, changed_files: List[str]
) -> List[ParsedIssue]:
    """Parse agent output to extract structured issues with file/line info and code suggestions."""
    issues = []
    lines = agent_output.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        pattern = r"`([^`]+):(\d+)`\s*-\s*(.+)"
        match = re.search(pattern, line)

        if match:
            file_path = match.group(1)
            line_num = int(match.group(2))
            description = match.group(3).strip()

            severity = "MEDIUM"
            if "critical" in line.lower():
                severity = "CRITICAL"
            elif "high" in line.lower():
                severity = "HIGH"
            elif "low" in line.lower():
                severity = "LOW"

            current_code = None
            suggestion = None

            for j in range(i + 1, min(i + 10, len(lines))):
                next_line = lines[j].strip()

                if re.search(r"`[^`]+:\d+`", next_line):
                    break

                if not current_code:
                    current_patterns = [
                        r"\*\*Current code:\*\*\s*`(.+?)`",
                        r"- \*\*Current code:\*\*\s*`(.+?)`",
                        r"Current code:\s*`(.+?)`",
                    ]
                    for pattern in current_patterns:
                        current_match = re.search(pattern, next_line)
                        if current_match:
                            current_code = current_match.group(1).strip()
                            break

                if not suggestion:
                    fix_patterns = [
                        r"\*\*Fix:\*\*\s*`(.+?)`",
                        r"\*\*Optimization:\*\*\s*`(.+?)`",
                        r"- \*\*Fix:\*\*\s*`(.+?)`",
                        r"Fix:\s*`(.+?)`",
                    ]
                    for pattern in fix_patterns:
                        fix_match = re.search(pattern, next_line)
                        if fix_match:
                            suggestion = fix_match.group(1).strip()
                            break

            if any(file_path in changed_file for changed_file in changed_files):
                if suggestion or current_code:
                    issues.append(
                        ParsedIssue(
                            file_path,
                            line_num,
                            severity,
                            description,
                            current_code,
                            suggestion,
                        )
                    )

        i += 1

    return issues


async def aggregator_agent(state: dict) -> dict:
    """Aggregator agent - combines all agent outputs - returns only updated keys"""
    try:
        security_analysis = state.get("security_analysis", "")
        code_quality_analysis = state.get("code_quality_analysis", "")
        performance_analysis = state.get("performance_analysis", "")
        changed_files = state.get("changed_files", [])

        failed_agents = []
        if state.get("security_agent_status") == AgentStatus.FAILED:
            failed_agents.append("Security")
        if state.get("code_quality_agent_status") == AgentStatus.FAILED:
            failed_agents.append("Code Quality")
        if state.get("performance_agent_status") == AgentStatus.FAILED:
            failed_agents.append("Performance")

        security_issues = parse_agent_issues(security_analysis, changed_files)
        code_quality_issues = parse_agent_issues(code_quality_analysis, changed_files)
        performance_issues = parse_agent_issues(performance_analysis, changed_files)

        all_issues = security_issues + code_quality_issues + performance_issues

        summary, inline_comments_data = build_review_with_inline_comments(
            security_analysis,
            code_quality_analysis,
            performance_analysis,
            security_issues,
            performance_issues,
            code_quality_issues,
            failed_agents,
            state.get("pr_title", ""),
        )

        return {
            "final_review": summary,
            "inline_comments": inline_comments_data,
            "total_issues": len(all_issues),
            "aggregator_status": AgentStatus.COMPLETED,
        }
    except Exception as e:
        return {
            "aggregator_status": AgentStatus.FAILED,
            "errors": [f"Aggregator failed: {str(e)}"],
            "final_review": f"Review aggregation failed: {str(e)}",
            "inline_comments": [],
        }


def build_review_with_inline_comments(
    security_analysis: str,
    code_quality_analysis: str,
    performance_analysis: str,
    security_issues: List[ParsedIssue],
    performance_issues: List[ParsedIssue],
    code_quality_issues: List[ParsedIssue],
    failed_agents: List[str],
    pr_title: str,
) -> tuple[str, List[Dict]]:
    """Build summary review with code suggestions consolidated in one section"""

    # Group code quality issues by file for Code Suggestions section
    issues_by_file = {}
    for issue in code_quality_issues:
        if issue.file_path not in issues_by_file:
            issues_by_file[issue.file_path] = []
        issues_by_file[issue.file_path].append(issue)

    # Build summary with code suggestions inside
    summary = build_summary_review(
        security_analysis,
        code_quality_analysis,
        performance_analysis,
        security_issues,
        performance_issues,
        issues_by_file,
        failed_agents,
        pr_title,
    )

    # Return empty inline comments - everything goes in the summary
    return summary, []


def normalize_severity(severity: str) -> str:
    """Normalize severity to CRITICAL or MEDIUM"""
    if severity in ["CRITICAL", "HIGH"]:
        return "CRITICAL"
    else:
        return "MEDIUM"


def build_severity_grouped_section(issues: List[ParsedIssue], section_type: str) -> str:
    """Build severity-grouped section with code blocks and enhanced UI"""
    if not issues:
        return ""

    # Normalize and group by severity
    severity_groups = {"CRITICAL": [], "MEDIUM": []}
    for issue in issues:
        normalized = normalize_severity(issue.severity)
        severity_groups[normalized].append(issue)

    section_parts = []

    # Add alert box at the top
    total_count = len(issues)
    critical_count = len(severity_groups["CRITICAL"])

    if critical_count > 0:
        section_parts.append("\n> [!WARNING]")
        section_parts.append(
            f"> Found {total_count} {section_type.lower()} issue{'s' if total_count != 1 else ''} that need attention before merging.\n"
        )
    else:
        section_parts.append("\n> [!CAUTION]")
        section_parts.append(
            f"> Found {total_count} {section_type.lower()} issue{'s' if total_count != 1 else ''} to review.\n"
        )

    first_section = True
    for severity in ["CRITICAL", "MEDIUM"]:
        severity_issues = severity_groups[severity]
        if not severity_issues:
            continue

        # Add horizontal rule between sections
        if not first_section:
            section_parts.append("\n---\n")
        first_section = False

        # Add emoji and count to header
        emoji = "🔴" if severity == "CRITICAL" else "⚠️"
        count = len(severity_issues)
        section_parts.append(
            f"### {emoji} {severity} ({count} issue{'s' if count != 1 else ''})\n"
        )

        # Create impact summary
        descriptions = [issue.description for issue in severity_issues]
        summary = " ".join(descriptions[:2])  # Limit to first 2 descriptions
        if len(descriptions) > 2:
            summary += f" (and {len(descriptions) - 2} more)"
        section_parts.append(f"> **Impact:** {summary}\n")

        # Group by file
        issues_by_file = {}
        for issue in severity_issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Display code blocks per file
        for file_path, file_issues in issues_by_file.items():
            section_parts.append(f"\n📄 **{file_path}**\n```python")
            for issue in file_issues:
                if issue.current_code:
                    section_parts.append(
                        f"line {issue.line}: {issue.current_code.strip()}"
                    )
            section_parts.append("```\n")

    # Add tip at the end
    if critical_count > 0:
        section_parts.append("\n> [!TIP]")
        section_parts.append("> Fix CRITICAL issues before merging to production.\n")

    return "\n".join(section_parts)


def build_summary_review(
    security_analysis: str,
    code_quality_analysis: str,
    performance_analysis: str,
    security_issues: List[ParsedIssue],
    performance_issues: List[ParsedIssue],
    issues_by_file: Dict[str, List[ParsedIssue]],
    failed_agents: List[str],
    pr_title: str,
) -> str:
    """Build high-level summary review with collapsible sections"""
    review_parts = []

    total_issues = len(security_issues) + len(performance_issues) + len(issues_by_file)

    review_parts.append("## Code Review\n")

    if failed_agents:
        review_parts.append(f"*Note: {', '.join(failed_agents)} analysis failed*\n")

    if total_issues == 0:
        review_parts.append("**No critical issues found!** Code looks good.\n")
        review_parts.append("---")
        review_parts.append("*Generated by CodeBoss*")
        return "\n".join(review_parts)

    if code_quality_analysis and "No major quality" not in code_quality_analysis:
        review_parts.append("<details>")
        review_parts.append(
            "<summary><strong>🔍 Potential Issues Found</strong></summary>\n"
        )
        review_parts.append(code_quality_analysis)
        review_parts.append("\n</details>\n")

    if security_issues:
        review_parts.append("<details>")
        review_parts.append("<summary><strong>🔒 Security Issues</strong></summary>\n")
        review_parts.append(build_severity_grouped_section(security_issues, "security"))
        review_parts.append("\n</details>\n")

    if performance_issues:
        review_parts.append("<details>")
        review_parts.append(
            "<summary><strong>⚡ Performance Optimization</strong></summary>\n"
        )
        review_parts.append(
            build_severity_grouped_section(performance_issues, "performance")
        )
        review_parts.append("\n</details>\n")

    if issues_by_file:
        review_parts.append("<details>")
        review_parts.append("<summary><strong>💡 Code Suggestions</strong></summary>\n")

        for file_path, issues in issues_by_file.items():
            review_parts.append(f"\n`{file_path}`\n")

            issues_with_fixes = [issue for issue in issues if issue.suggestion]

            if not issues_with_fixes:
                continue

            review_parts.append("```diff")
            for issue in issues_with_fixes:
                if issue.current_code and issue.suggestion:
                    review_parts.append(
                        f"- {issue.line:4d}  {issue.current_code.strip()}"
                    )
                    review_parts.append(
                        f"+ {issue.line:4d}  {issue.suggestion.strip()}"
                    )
                elif issue.suggestion:
                    review_parts.append(
                        f"+ {issue.line:4d}  {issue.suggestion.strip()}"
                    )

            review_parts.append("```\n")

        review_parts.append("</details>\n")

    review_parts.append("---")
    review_parts.append("*Generated by CodeBoss*")

    return "\n".join(review_parts)
