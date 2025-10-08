from datetime import datetime


class EnhancedContextBuilder:
    """
    Enhanced context builder that integrates AST parser markdown output
    with existing PR history and diff analysis
    """

    def __init__(self):
        pass

    def create_ast_markdown_context(self, file_path: str, repo_path: str) -> str:
        """
        Creating markdown context from AST parser for a specific file
        """
        language = self._detect_language(file_path)
        if not language:
            return ""

        try:
            # Initializing AST parser for this language
            ast_parser = MultiLanguageAnalyzer(languag)

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

    def _detect_language(self, file_path: str) -> [str]:
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
        graph_stats = semantic_analysis.get("graph_stats", {})
        analysis_method = semantic_analysis.get("analysis_method", "unknown")

        markdown = f"""## Enhanced File Analysis: `{file_path}`

### Analysis Summary
- **Analysis Method**: {analysis_method}
- **Functions**: {len(detailed_functions)}
- **Classes**: {len(detailed_classes)}
- **Imports**: {len(detailed_imports)}
- **Semantic Graph Nodes**: {graph_stats.get('nodes', 0)}
- **Semantic Graph Edges**: {graph_stats.get('edges', 0)}

### Graph Statistics
- **Functions in Graph**: {graph_stats.get('functions', 0)}
- **Classes in Graph**: {graph_stats.get('classes', 0)}
- **Imports in Graph**: {graph_stats.get('imports', 0)}

"""
        if detailed_classes:
            markdown += "### Classes\n\n"
            for cls in detailed_classes:
                markdown += f"- **{cls['name']}** (line {cls['line']})\n"
            markdown += "\n"

        # Add functions with complete code and enhanced semantic info
        if detailed_functions:
            markdown += "### Functions with Complete Code & Semantic Analysis\n\n"

            for func in detailed_function:
                func_name  func["function_name"]

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

**📊 Semantic Analysis:**
- **Function Calls**: {', '.join(func_deps) if func_deps else 'None'}
- **Imports Used**: {', '.join(func_imports) if func_imports else 'None'}
- **Code Lines**: {func.get('code_lines', 'N/A')}

---
"""

        # Enhanced dependency graph with semantic information
        if function_dependencies:
            markdown += "### Enhanced Function Dependencies (from Semantic Graph)\n\n"
            for caller, callees in function_dependencies.items():
                if callees:
                    for callee in callees:
                        markdown += f"- **{caller}()** → **{callee}()**\n"
                else:
                    markdown += f"- **{caller}()** (no internal calls)\n"
            markdown += "\n"

        # Enhanced import usage analysis
        if import_usage:
            markdown += "### Import Usage Analysis (from Semantic Graph)\n\n"
            for func_name, imports_used in import_usage.items():
                if imports_used:
                    markdown += f"- **{func_name}()** uses: {', '.join(imports_used)}\n"
            markdown += "\n"

        # Adding imports with enhanced information
        if detailed_imports:
            markdown += "### All Imports Used\n\n"
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

        context = "## Enhanced Code Analysis (Semantic Graph + Detailed AST)\n\n"

        diff_files = diff_data.get("diff_files", [])
        analyzed_files = 0

        # Prioritizing Python, JavaScript, and TypeScript files
        priority_extensions = [".py", ".js", ".ts"]
        prioritized_files = []
        other_files = []

        for file_path in diff_files:
            if any(file_path.endswith(ext) for ext in priority_extensions):
                prioritized_files.append(file_path)
            else:
                other_files.append(file_path)

        # Analyzing prioritized files first, then others
        files_to_analyze = prioritized_files + other_files  # All files

        for file_path in files_to_analyze:
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
