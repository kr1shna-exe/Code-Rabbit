from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .simple_ast_parser import LANGUAGE_MAP, LANGUAGE_MODULES, SimpleASTParser
from .simple_semantics import build_simple_graph


class SimpleContextBuilder:
    """
    Simplified context builder that provides core functionality:
    1. Git diff for changed files
    2. Import resolution and source code collection
    3. Basic code graph generation
    4. Integration with GitHub history
    5. Clean output formatting
    """

    def __init__(self):
        pass

    def build_comprehensive_context(
        self, diff_data: Dict[str, Any], pr_history: Dict[str, Any], repo_path: str
    ) -> str:
        context_parts = []
        context_parts.append(self._build_pr_header(diff_data, pr_history))

        # Changed files analysis
        changed_files = diff_data.get("diff_files", [])
        for file_path in changed_files:
            full_path = Path(repo_path) / file_path
            if not full_path.exists():
                context_parts.append(
                    f"## File Analysis: {file_path}\n\n**File not found**: {file_path}\n"
                )
                continue

            try:
                # Detect language and handle unsupported files
                language = self._detect_language(file_path)

                # Skip if language not supported
                if language not in LANGUAGE_MODULES:
                    context_parts.append(
                        f"## File Analysis: {file_path}\n\n**Language not supported**: {language}\n"
                    )
                    continue

                # Parse the file
                parser = SimpleASTParser(language)
                tree, source_code = parser.parse_file(str(full_path))

                # Extract basic information
                semantic_analysis = parser.extract_semantic_analysis(
                    tree, source_code, file_path
                )

                # Build simple graph
                graph = build_simple_graph(
                    tree, source_code, semantic_analysis["language"], file_path
                )

                # Extract graph insights for AI
                graph_insights = self._extract_graph_insights(graph)

                # Resolve cross-file dependencies
                cross_file_deps = self._resolve_simple_dependencies(
                    semantic_analysis, repo_path, file_path
                )

                # Add to context
                context_parts.append(
                    self._build_file_analysis(
                        file_path,
                        diff_data,
                        semantic_analysis,
                        cross_file_deps,
                        graph_insights,
                    )
                )
            except Exception as e:
                context_parts.append(
                    f"## File Analysis: {file_path}\n\n**Error**: {str(e)}\n\n**File content preview**:\n```\n"
                )
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        preview = (
                            content[:500] + "..." if len(content) > 500 else content
                        )
                        context_parts.append(preview)
                except Exception as e:
                    print(f"Warning: Could not read file content: {e}")
                    context_parts.append("Could not read file content")

                context_parts.append("\n```")

        # Cross-file dependencies section
        all_dependencies = self._collect_all_dependencies(changed_files, repo_path)
        if all_dependencies:
            context_parts.append(self._build_dependencies_section(all_dependencies))

        # Summary
        context_parts.append(self._build_summary(diff_data, pr_history))

        return "\n\n".join(context_parts)

    def _build_pr_header(
        self, diff_data: Dict[str, Any], pr_history: Dict[str, Any]
    ) -> str:
        pr_info = pr_history.get("pr_info", {})
        commits = pr_history.get("commits", [])
        comments = pr_history.get("all_comments", [])
        maintainers = pr_history.get("maintainers", [])
        maintainer_reviews = [
            c for c in comments if c.get("type") == "maintainer_review"
        ]
        bot_reviews = [c for c in comments if c.get("type") == "bot_review"]

        header = f"""# Pull Request Analysis

## PR Information
- **Title**: {pr_info.get('title', 'No title')}
- **Description**: {(pr_info.get('description') or 'No description')[:200]}...
- **Author**: {pr_info.get('author', 'Unknown')}
- **State**: {pr_info.get('state', 'Unknown')}
- **Files Changed**: {len(diff_data.get('diff_files', []))}
- **Base Branch**: {diff_data.get('base_branch', 'main')}
- **Head Branch**: {diff_data.get('head_branch', 'feature')}
- **Repository Maintainers**: {', '.join(maintainers) if maintainers else 'None found'}
- **Maintainer Reviews**: {len(maintainer_reviews)}
- **Bot Reviews**: {len(bot_reviews)}

## PR History Context

### Recent Activity
- **Total Commits**: {len(commits)}
- **Total Comments**: {len(comments)}

### Latest Commit
"""

        if commits:
            latest_commit = commits[0]
            header += f"""- **Message**: {latest_commit.get('message', 'No message')}
- **Author**: {latest_commit.get('author', 'Unknown')}
- **Date**: {latest_commit.get('date', 'Unknown')}"""

        return header

    def _build_file_analysis(
        self,
        file_path: str,
        diff_data: Dict[str, Any],
        semantic_analysis: Dict[str, Any],
        cross_file_deps: Dict[str, Any],
        graph_insights: Dict[str, Any],
    ) -> str:
        """Build analysis for a single file."""
        functions = semantic_analysis.get("functions", [])
        classes = semantic_analysis.get("classes", [])
        imports = semantic_analysis.get("imports", [])

        analysis = f"""## File Analysis: {file_path}

**Language**: {semantic_analysis.get('language', 'unknown')}
**Functions**: {len(functions)}
**Classes**: {len(classes)}
**Imports**: {len(imports)}

### Functions & Classes
"""

        # Add functions
        for func in functions[:5]:  # Limit to first 5
            analysis += f"- **{func['name']}** (line {func['start_line']})\n"

        if len(functions) > 5:
            analysis += f"- ... and {len(functions) - 5} more functions\n"

        # Add classes
        for cls in classes[:3]:  # Limit to first 3
            analysis += f"- **{cls['name']}** (line {cls['start_line']})\n"

        if len(classes) > 3:
            analysis += f"- ... and {len(classes) - 3} more classes\n"

        # Add imports
        if imports:
            analysis += "\n### Imports\n"
            for imp in imports[:10]:  # Limit to first 10
                analysis += f"- `{imp}`\n"
            if len(imports) > 10:
                analysis += f"- ... and {len(imports) - 10} more imports\n"

        # Add graph insights
        if graph_insights:
            analysis += "\n### Code Graph Analysis\n"
            analysis += (
                f"- **Functions found**: {graph_insights.get('function_count', 0)}\n"
            )
            analysis += f"- **Classes found**: {graph_insights.get('class_count', 0)}\n"
            analysis += (
                f"- **Import statements**: {graph_insights.get('import_count', 0)}\n"
            )

            if graph_insights.get("function_calls"):
                analysis += f"- **Function calls detected**: {', '.join(graph_insights['function_calls'][:5])}\n"

            if graph_insights.get("relationships"):
                analysis += f"- **Code relationships**: {graph_insights['relationships']} total connections\n"

        # Add git diff
        file_diff = diff_data.get("full_diff", "")
        if file_diff:
            analysis += f"\n### Git Diff\n```\n{file_diff}\n```"

        return analysis

    def _extract_graph_insights(self, graph) -> Dict[str, Any]:
        if not graph:
            return {}

        insights = {
            "function_count": 0,
            "class_count": 0,
            "import_count": 0,
            "function_calls": [],
            "relationships": 0,
        }

        # Count different types of nodes
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get("type", "")

            if node_type == "function":
                insights["function_count"] += 1
            elif node_type == "class":
                insights["class_count"] += 1
            elif node_type == "import":
                insights["import_count"] += 1
            elif node_type == "call":
                func_name = node_data.get("name", "")
                if func_name and func_name not in insights["function_calls"]:
                    insights["function_calls"].append(func_name)

        # Count relationships (edges)
        insights["relationships"] = graph.number_of_edges()

        return insights

    def _resolve_simple_dependencies(
        self, semantic_analysis: Dict[str, Any], repo_path: str, current_file: str
    ) -> Dict[str, Any]:
        imports = semantic_analysis.get("imports", [])
        dependencies = []

        for import_name in imports:
            potential_paths = [
                f"{import_name.replace('.', '/')}.py",  # Direct path (for external repos)
                f"src/{import_name.replace('.', '/')}.py",  # src/ path (for our repo)
            ]

            # Skip if it's a relative import starting with dots
            if import_name.startswith("."):
                continue

            for potential_path in potential_paths:
                full_path = Path(repo_path) / potential_path

                if full_path.exists():
                    # Read the source code
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            source_code = f.read()

                        dependencies.append(
                            {
                                "import_name": import_name,
                                "resolved_path": potential_path,
                                "source_code": source_code,
                                "size": len(source_code),
                            }
                        )
                        break  # Stop after finding the first match
                    except Exception as e:
                        print(f"Error reading source code for {import_name}: {e}")
                        continue

        return {"dependencies": dependencies, "count": len(dependencies)}

    def _collect_all_dependencies(
        self, changed_files: List[str], repo_path: str
    ) -> List[Dict[str, Any]]:
        all_deps = set()
        dependency_files = []

        for file_path in changed_files:
            full_path = Path(repo_path) / file_path
            if not full_path.exists():
                continue

            try:
                parser = SimpleASTParser(self._detect_language(file_path))
                tree, source_code = parser.parse_file(str(full_path))
                semantic_analysis = parser.extract_semantic_analysis(
                    tree, source_code, file_path
                )

                cross_file_deps = self._resolve_simple_dependencies(
                    semantic_analysis, repo_path, file_path
                )

                deps_found = cross_file_deps.get("dependencies", [])

                for dep in deps_found:
                    resolved_path = dep["resolved_path"]
                    if (
                        resolved_path not in all_deps
                        and resolved_path not in changed_files
                    ):
                        all_deps.add(resolved_path)
                        dependency_files.append(dep)

            except Exception as e:
                print(f"Error collecting dependencies for {file_path}: {e}")
                continue
        return dependency_files

    def _build_dependencies_section(self, dependencies: List[Dict[str, Any]]) -> str:
        """Build cross-file dependencies section."""
        section = f"""## Cross-File Dependencies

**Additional files imported by changed code**: {len(dependencies)}

"""

        for dep in dependencies[:10]:  # Limit to first 10
            section += f"""### {dep['resolved_path']}
**Import**: `{dep['import_name']}`
**Size**: {dep['size']} characters

#### Source Code
```python
{dep['source_code'][:1000]}{'...' if len(dep['source_code']) > 1000 else ''}
```

"""

        if len(dependencies) > 10:
            section += f"... and {len(dependencies) - 10} more dependency files\n"

        return section

    def _build_summary(
        self, diff_data: Dict[str, Any], pr_history: Dict[str, Any]
    ) -> str:
        """Build summary section."""
        changed_files = diff_data.get("diff_files", [])
        commits = pr_history.get("commits", [])
        comments = pr_history.get("all_comments", [])

        summary = f"""## Summary

- **Total files changed**: {len(changed_files)}
- **Total commits**: {len(commits)}
- **Total comments**: {len(comments)}

**Files changed**:
"""

        for file_path in changed_files:
            summary += f"- `{file_path}`\n"

        summary += f"""
**Analysis completed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return summary

    def _detect_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        return LANGUAGE_MAP.get(ext, "python")
