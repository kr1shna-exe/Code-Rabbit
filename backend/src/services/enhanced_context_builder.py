import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .ast_parser import MultiLanguageAnalyzer
from .semantics import analyze_semantics


class EnhancedContextBuilder:
    """
    Enhanced context builder that integrates AST parser markdown output
    with existing PR history and diff analysis
    """

    def __init__(self):
        pass

    def _resolve_cross_file_dependencies(
        self, semantic_analysis: Dict[str, Any], repo_path: str
    ) -> Dict[str, Any]:
        """
        Simple cross-file dependency resolution.
        Matches function calls to imports and fetches source code.
        """
        imports_map = semantic_analysis.get("imports_map", {})
        function_calls = semantic_analysis.get("function_calls", [])

        cross_file_deps = []

        for call in function_calls:
            called_func = call.get("called_function")
            calling_func = call.get("calling_function")
            line = call.get("line")

            # Check if this function call matches an import
            # Extract base function name (e.g., "settings" from "settings.get_database_url")
            base_func_name = called_func.split('.')[0] if '.' in called_func else called_func
            if base_func_name in imports_map:
                module_name = imports_map[base_func_name]

                # Resolve file path (simple conversion)
                target_file = self._resolve_module_path(module_name, repo_path)

                if target_file and Path(target_file).exists():
                    # Fetch source code
                    source_code = self._read_file_content(target_file)

                    if source_code:
                        cross_file_deps.append(
                            {
                                "calling_function": calling_func,
                                "called_function": called_func,
                                "line": line,
                                "target_file": target_file,
                                "target_source_code": source_code,
                                "module_name": module_name,
                            }
                        )

        return cross_file_deps

    def _resolve_module_path(self, module_name: str, repo_path: str) -> Optional[str]:
        """
        Simple module path resolution.
        Converts module names to file paths.
        """
        if not module_name:
            return None

        # Try common patterns
        potential_paths = [
            f"{module_name.replace('.', '/')}.py",
            f"{module_name.replace('.', '/')}/__init__.py",
            f"{module_name}.py",
            f"backend/src/{module_name.replace('.', '/')}.py",
            f"backend/src/{module_name.replace('.', '/')}/__init__.py",
        ]

        for path in potential_paths:
            full_path = Path(repo_path) / path
            if full_path.exists():
                return str(full_path)

        return None

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        Simple file content reader.
        """
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
            return None

    def create_ast_markdown_context(self, file_path: str, repo_path: str) -> str:
        """
        Creating markdown context from AST parser for a specific file
        """
        language = self._detect_language(file_path)
        if not language:
            return ""

        try:
            # Initializing AST parser for this language
            ast_parser = MultiLanguageAnalyzer(language)

            # Read and analyze the file
            full_path = Path(repo_path) / file_path
            if not full_path.exists():
                return f"File not found: {file_path}"

            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Parsing and extracting information
            tree = ast_parser.parse_code(code)

            # Use enhanced semantic analysis (combining both approaches)
            semantic_analysis = ast_parser.extract_semantic_analysis(
                tree, code, file_path
            )

            # Perform deep semantic analysis using the new semantics module
            deep_semantics = analyze_semantics(code, file_path)

            # Resolve cross-file dependencies using simple logic
            cross_file_deps = self._resolve_cross_file_dependencies(
                deep_semantics, repo_path
            )

            # Merge semantic analysis with deep semantics and cross-file resolution
            if deep_semantics.get("analysis_type") == "semantic":
                semantic_analysis.update(
                    {
                        "deep_semantics": deep_semantics,
                        "semantic_insights": deep_semantics.get(
                            "semantic_insights", []
                        ),
                        "security_patterns": deep_semantics.get(
                            "security_patterns", []
                        ),
                        "semantic_graph": deep_semantics.get("semantic_graph", {}),
                        "function_complexity": deep_semantics.get(
                            "function_complexity", {}
                        ),
                        "cross_file_dependencies": cross_file_deps,
                        "imports_map": deep_semantics.get("imports_map", {}),
                        "analysis_method": "enhanced_semantic_with_cross_file",
                    }
                )
            else:
                semantic_analysis["analysis_method"] = "ast_only"

            # For backward compatibility, extract individual components
            functions = semantic_analysis.get("detailed_functions", [])
            imports = semantic_analysis.get("detailed_imports", [])
            dependencies = semantic_analysis.get("function_dependencies", {})
            classes = semantic_analysis.get("detailed_classes", [])

            # Convert to enhanced markdown with semantic information
            markdown = self._convert_to_enhanced_markdown(file_path, semantic_analysis)

            return markdown

        except Exception as e:
            return f"AST analysis failed for {file_path}: {str(e)}"

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
        }
        return language_map.get(ext)

    def _convert_to_enhanced_markdown(
        self, file_path: str, semantic_analysis: Dict
    ) -> str:
        """Convert enhanced semantic analysis to markdown format with graph information"""

        # Extract components from semantic analysis
        detailed_functions = semantic_analysis.get("detailed_functions", [])
        detailed_imports = semantic_analysis.get("detailed_imports", [])
        detailed_classes = semantic_analysis.get("detailed_classes", [])
        function_dependencies = semantic_analysis.get("function_dependencies", {})
        import_usage = semantic_analysis.get("import_usage", {})
        analysis_method = semantic_analysis.get("analysis_method", "unknown")
        semantic_insights = semantic_analysis.get("semantic_insights", [])
        security_patterns = semantic_analysis.get("security_patterns", [])
        function_complexity = semantic_analysis.get("function_complexity", {})
        semantic_graph = semantic_analysis.get("semantic_graph", {})
        # Get graph_stats from top level (where ast_parser stores it) or from semantic_graph
        graph_stats = semantic_analysis.get("graph_stats", semantic_graph.get("graph_stats", {}))
        cross_file_dependencies = semantic_analysis.get("cross_file_dependencies", [])

        markdown = f"""## Enhanced File Analysis: `{file_path}`

### Analysis Summary
- **Analysis Method**: {analysis_method}
- **Functions**: {len(detailed_functions)}
- **Classes**: {len(detailed_classes)}
- **Imports**: {len(detailed_imports)}
- **Semantic Graph Nodes**: {graph_stats.get('total_nodes', 0)}
- **Semantic Graph Edges**: {graph_stats.get('total_edges', 0)}

"""

        # Add semantic insights if available
        if semantic_insights:
            markdown += "### Semantic Insights\n\n"
            for insight in semantic_insights:
                markdown += f"- **{insight.get('type', 'Unknown').replace('_', ' ').title()}**: {insight.get('message', 'No message')}\n"
            markdown += "\n"

        # Add security patterns if available
        if security_patterns:
            markdown += "### Security Analysis\n\n"
            for pattern in security_patterns:
                markdown += f"- **{pattern.get('type', 'Unknown').replace('_', ' ').title()}** (line {pattern.get('line', 'N/A')})\n"
                if pattern.get("value"):
                    markdown += f"  - Value: `{pattern.get('value')}`\n"
                if pattern.get("function"):
                    markdown += f"  - Function: `{pattern.get('function')}`\n"
            markdown += "\n"

        # Add function complexity analysis
        if function_complexity:
            markdown += "### Function Complexity\n\n"
            for func_name, complexity in function_complexity.items():
                complexity_level = (
                    "High" if complexity > 10 else "Medium" if complexity > 5 else "Low"
                )
                markdown += f"- **{func_name}()**: Complexity {complexity} ({complexity_level})\n"
            markdown += "\n"
        if detailed_classes:
            markdown += "### Classes\n\n"
            for cls in detailed_classes:
                markdown += f"- **{cls['name']}** (line {cls['line']})\n"
            markdown += "\n"

        # Add functions with complete code and enhanced semantic info
        if detailed_functions:
            markdown += "### Functions with Complete Code & Semantic Analysis\n\n"

            for func in detailed_functions:
                func_name = func["name"]

                # Enhanced import usage from semantic analysis
                func_imports = import_usage.get(func_name, [])

                # Enhanced dependencies from semantic analysis
                func_deps = function_dependencies.get(func_name, [])

                markdown += f"""#### {func['name']} (line {func['line']})

**Signature:** `{func['signature']}`

**Complete Code:**
```python
{func['complete_code']}
```

**Semantic Analysis:**
- **Function Calls**: {', '.join(func_deps) if func_deps else 'None'}
- **Imports Used**: {', '.join(func_imports) if func_imports else 'None'}
- **Code Lines**: {func.get('code_lines', 'N/A')}

---
"""

        # Function dependencies
        if function_dependencies:
            markdown += "### Function Dependencies\n\n"
            for caller, callees in function_dependencies.items():
                if callees:
                    for callee in callees:
                        markdown += f"- **{caller}()** → **{callee}()**\n"
                else:
                    markdown += f"- **{caller}()** (no internal calls)\n"
            markdown += "\n"

        # Import usage analysis
        if import_usage:
            markdown += "### Import Usage\n\n"
            for func_name, imports_used in import_usage.items():
                if imports_used:
                    markdown += f"- **{func_name}()** uses: {', '.join(imports_used)}\n"
            markdown += "\n"

        # Cross-File Dependencies
        if cross_file_dependencies:
            markdown += "### Cross-File Dependencies\n\n"
            for dep in cross_file_dependencies:
                calling_func = dep.get("calling_function", "Unknown")
                called_func = dep.get("called_function", "Unknown")
                line = dep.get("line", "Unknown")
                target_file = dep.get("target_file", "Unknown")
                module_name = dep.get("module_name", "Unknown")
                source_code = dep.get("target_source_code", "")

                markdown += f"""#### {calling_func}() calls {called_func}() (line {line})

**Import from module:** `{module_name}`
**Source file:** `{target_file}`

**Source Code:**
```python
{source_code}
```

---
"""

        # Imports
        if detailed_imports:
            markdown += "### All Imports\n\n"
            for imp in detailed_imports:
                markdown += f"- **{imp['module']}** ({imp['type']} import, line {imp['line']})\n"
            markdown += "\n"

        return markdown

    def build_comprehensive_ai_context(
        self, diff_data: Dict, pr_history: Dict, repo_path: str
    ) -> str:
        """
        Build comprehensive AI context combining:
        1. PR diff/code changes
        2. PR history (commits, bot comments)
        3. AST parser markdown analysis
        """
        try:
            context_parts = []

            # PR Information
            pr_title = diff_data.get("pr_title", "N/A")
            pr_description = diff_data.get("pr_description", "No description provided")

            context_parts.append(
                f"""# Pull Request Analysis

## PR Information
- **Title**: {pr_title}
- **Description**: {pr_description}
- **Files Changed**: {len(diff_data.get('diff_files', []))}
- **Base Branch**: {diff_data.get('base_branch', 'main')}
- **Head Branch**: {diff_data.get('head_branch', 'feature')}

"""
            )

            # PR History Context
            context_parts.append(self._format_pr_history(pr_history))

            # Code Changes (Diff)
            context_parts.append(self._format_code_changes(diff_data))

            # AST Analysis for changed files
            context_parts.append(
                self._build_ast_analysis_for_changed_files(diff_data, repo_path)
            )

            # Combining all the parts
            full_context = "\n".join(context_parts)

            # Adding final instructions for AI
            full_context += """

## AI Instructions

Please provide a comprehensive code review that considers:

1. **Code Quality**: Best practices, patterns, potential improvements
2. **Security**: Any security vulnerabilities or concerns
3. **Performance**: Performance implications and optimizations
4. **Dependencies**: Impact of new imports and function dependencies
5. **Maintainability**: Code readability and future maintenance
6. **Testing**: Testability and testing suggestions

Focus on the changed functions and their dependencies. Consider the PR history to avoid repeating previous suggestions.

---
*Context generated by enhanced AST parser + PR history analysis*
"""

            return full_context

        except Exception as e:
            return f"""# Pull Request Analysis

## Enhanced Context Building Failed

**Error**: {str(e)}

## Basic PR Information
- **Title**: {diff_data.get('pr_title', 'N/A')}
- **Files Changed**: {len(diff_data.get('diff_files', []))}

## Code Changes (Diff)
```diff
{diff_data.get('full_diff', '')}
```

---
*Falling back to basic diff analysis due to context building error*
"""

        return full_context

    def _format_pr_history(self, pr_history: Dict) -> str:
        """Format PR history for AI context"""

        context = "## PR History Context\n\n"

        # PR info
        pr_info = pr_history.get("pr_info", {})
        context += f"""### PR Details
- **Author**: {pr_info.get('author', 'Unknown')}
- **State**: {pr_info.get('state', 'Unknown')}
- **Created**: {pr_info.get('created_at', 'Unknown')}
- **Base Branch**: {pr_info.get('base_branch', 'main')}

"""

        # Recent commits
        commits = pr_history.get("commits", [])[:3]  # Only Last 3 commits
        if commits:
            context += "### Recent Commits\n\n"
            for commit in commits:
                context += f"""**{commit['sha']}** - {commit['author']} ({commit['date']})
- **Files**: {', '.join(commit['files_changed'])}
- **Message**: {commit['message']}

"""

        # Bot comments
        bot_comments = pr_history.get("all_comments", [])
        if bot_comments:
            context += "### Previous AI Suggestions\n\n"
            for comment in bot_comments[-3:]:  # Only Last 3 comments
                context += f"""**{comment['author']}** ({comment['created_at']}):
{comment['comment']}

"""

        return context

    def _format_code_changes(self, diff_data: Dict) -> str:
        """Format code changes for AI context"""

        context = "## Code Changes (Diff)\n\n"

        # Full diff
        full_diff = diff_data.get("full_diff", "")
        if full_diff:
            context += "### Complete Diff\n\n```diff\n"
            context += full_diff
            context += "\n```\n\n"

        # Changed files summary
        diff_files = diff_data.get("diff_files", [])
        if diff_files:
            context += "### Changed Files\n\n"
            for file_path in diff_files:
                context += f"- `{file_path}`\n"
            context += "\n"

        return context

    def _build_ast_analysis_for_changed_files(
        self, diff_data: Dict, repo_path: str
    ) -> str:
        """Build AST analysis markdown for all changed files"""

        context = "## Enhanced Code Analysis\n\n"

        diff_files = diff_data.get("diff_files", [])
        analyzed_files = 0

        # Prioritizing Python, JavaScript, and TypeScript files
        priority_extensions = [".py", ".js", ".ts"]

        for file_path in diff_files:
            if any(file_path.endswith(ext) for ext in priority_extensions):
                ast_context = self.create_ast_markdown_context(file_path, repo_path)
                if (
                    ast_context
                    and not ast_context.startswith("File not found")
                    and not ast_context.startswith("AST analysis failed")
                ):
                    context += ast_context + "\n"
                    analyzed_files += 1

        if analyzed_files == 0:
            context += "*No supported files found for AST analysis*\n\n"

        return context
