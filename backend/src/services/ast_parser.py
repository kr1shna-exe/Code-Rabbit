import re
from typing import Any, Dict, List, Optional

import tree_sitter_go as tsgo
import tree_sitter_javascript as tsjs
import tree_sitter_python as tspython
import tree_sitter_rust as tsrust
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser, Query, QueryCursor

from .semantics import analyze_semantics


class MultiLanguageAnalyzer:
    LANGUAGES = {
        "python": tspython,
        "javascript": tsjs,
        "typescript": tsts,
        "go": tsgo,
        "rust": tsrust,
    }

    def __init__(self, language: str = "python"):
        if language not in self.LANGUAGES:
            raise ValueError(f"Unsupported: {language}")
        lang_module = self.LANGUAGES[language]
        self.language = Language(lang_module.language())
        self.parser = Parser(self.language)
        self.lang_name = language

    def parse_code(self, code: str):
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree

    def extract_classes(self, tree):
        """Extracting class definitions from AST"""

        queries = {
            "python": """
                (class_definition
                    name: (identifier) @class.name
                )
            """,
            "javascript": """
                (class_declaration
                    name: (identifier) @class.name
                )
            """,
            "typescript": """
                (class_declaration
                    name: (identifier) @class.name
                )
                (interface_declaration
                    name: (type_identifier) @class.name
                )
            """,
            "go": "",
            "rust": """
                (struct_item
                    name: (type_identifier) @class.name
                )
                (impl_item
                    type: (type_identifier) @class.name
                )
                (enum_item
                    name: (type_identifier) @class.name
                )
            """,
        }

        query_str = queries.get(self.lang_name, "")
        if not query_str:
            return []

        try:
            query = Query(self.language, query_str)
            cursor = QueryCursor(query)
            captures = cursor.captures(tree.root_node)

            classes = []
            for capture_name, nodes in captures.items():
                if "class.name" in capture_name:
                    for node in nodes:
                        classes.append(
                            {
                                "name": node.text.decode("utf8"),
                                "line": node.start_point[0] + 1,
                            }
                        )
            return classes
        except Exception as e:
            print(f"Warning: Class extraction failed for {self.lang_name}: {e}")
            return []

    def extract_functions(self, tree, code: str = None):
        """Extracting functions with complete code content"""

        queries = {
            "python": """
                (function_definition
                    name: (identifier) @function.name
                ) @function.def
            """,
            "javascript": """
                (function_declaration
                    name: (identifier) @function.name
                ) @function.def
                (function_expression
                    name: (identifier) @function.name
                ) @function.def
            """,
            "typescript": """
                (function_declaration
                    name: (identifier) @function.name
                ) @function.def
                (method_definition
                    name: (property_identifier) @function.name
                ) @function.def
            """,
            "go": """
                (function_declaration
                    name: (identifier) @function.name
                ) @function.def
                (method_declaration
                    name: (field_identifier) @function.name
                ) @function.def
            """,
            "rust": """
                (function_item
                    name: (identifier) @function.name
                ) @function.def
            """,
        }

        # For functions without complete definitions (like arrow functions)
        simple_queries = {
            "javascript": """
                (arrow_function) @function.arrow
            """,
        }

        functions = []

        # Splitting code into lines if provided
        code_lines = code.split("\n") if code else None

        # Extracting complete function definitions
        try:
            query = Query(self.language, queries[self.lang_name])
            query_cursor = QueryCursor(query)
            captures = query_cursor.captures(tree.root_node)

            for capture_name, nodes in captures.items():
                if "function.def" in capture_name:
                    for node in nodes:
                        func_node = node  # This is the complete function definition
                        name_node = None

                        # Find the function name within the function definition
                        for child in func_node.children:
                            if (
                                self.lang_name == "python"
                                and child.type == "identifier"
                            ):
                                name_node = child
                                break
                            elif (
                                self.lang_name in ["javascript", "typescript"]
                                and child.type == "identifier"
                            ):
                                name_node = child
                                break
                            elif self.lang_name == "go" and child.type == "identifier":
                                name_node = child
                                break
                            elif (
                                self.lang_name == "rust" and child.type == "identifier"
                            ):
                                name_node = child
                                break

                        if name_node:
                            func_name = name_node.text.decode("utf8")
                            line_num = name_node.start_point[0] + 1

                            # Extracting complete function code
                            start_byte = func_node.start_byte
                            end_byte = func_node.end_byte
                            complete_code = code[start_byte:end_byte] if code else ""

                            full_line = ""
                            if code_lines and line_num <= len(code_lines):
                                full_line = code_lines[line_num - 1]

                            functions.append(
                                {
                                    "name": func_name,
                                    "line": line_num,
                                    "full_line": full_line,
                                    "signature": full_line.strip(),
                                    "complete_code": complete_code,
                                    "start_byte": start_byte,
                                    "end_byte": end_byte,
                                    "start_point": func_node.start_point,
                                    "end_point": func_node.end_point,
                                    "code_lines": len(complete_code.split("\n")),
                                }
                            )

        except Exception as e:
            print(
                f"Warning: Complete function extraction failed for {self.lang_name}: {e}"
            )

        # Extracting simple functions (arrow functions, etc.)
        try:
            if self.lang_name in simple_queries:
                simple_query = Query(self.language, simple_queries[self.lang_name])
                simple_cursor = QueryCursor(simple_query)
                simple_captures = simple_cursor.captures(tree.root_node)

                for capture_name, nodes in simple_captures.items():
                    if "function.arrow" in capture_name:
                        for node in nodes:
                            line_num = node.start_point[0] + 1
                            start_byte = node.start_byte
                            end_byte = node.end_byte
                            complete_code = code[start_byte:end_byte] if code else ""

                            full_line = ""
                            if code_lines and line_num <= len(code_lines):
                                full_line = code_lines[line_num - 1]

                            # Generate name for anonymous functions
                            func_name = f"arrow_function_at_line_{line_num}"

                            functions.append(
                                {
                                    "name": func_name,
                                    "line": line_num,
                                    "full_line": full_line,
                                    "signature": full_line.strip(),
                                    "complete_code": complete_code,
                                    "start_byte": start_byte,
                                    "end_byte": end_byte,
                                    "start_point": node.start_point,
                                    "end_point": node.end_point,
                                    "code_lines": len(complete_code.split("\n")),
                                }
                            )

        except Exception as e:
            print(
                f"Warning: Simple function extraction failed for {self.lang_name}: {e}"
            )

        return functions

    def extract_imports(self, tree):
        """Extracting import statements from AST"""

        queries = {
            "python": """
                (import_statement
                    name: (dotted_name) @import.module
                )
                (import_from_statement
                    module_name: (dotted_name) @import.from
                )
            """,
            "javascript": """
                (import_statement
                    source: (string) @import.module
                )
                (require
                    arguments: (arguments (string) @import.module)
                )
            """,
            "typescript": """
                (import_statement
                    source: (string) @import.module
                )
                (import_statement
                    module: (identifier) @import.module
                )
            """,
            "go": """
                (import_spec
                    path: (interpreted_string_literal) @import.module
                )
            """,
            "rust": """
                (use_declaration
                    argument: (use_path) @import.module
                )
            """,
        }

        query_str = queries.get(self.lang_name, "")
        if not query_str:
            return []

        try:
            query = Query(self.language, query_str)
            query_cursor = QueryCursor(query)
            captures = query_cursor.captures(tree.root_node)

            imports = []
            for capture_name, nodes in captures.items():
                for node in nodes:
                    module_name = node.text.decode("utf8").strip("\"'")
                    imports.append(
                        {
                            "module": module_name,
                            "line": node.start_point[0] + 1,
                            "type": "from" if "from" in capture_name else "direct",
                        }
                    )
            return imports
        except Exception as e:
            print(f"Warning: Import extraction failed for {self.lang_name}: {e}")
            return []

    def extract_dependencies(self, tree, code: str = None):
        """
        DEPRECATED: Use extract_semantic_analysis() for better dependency analysis.
        This method is kept for backward compatibility but semantic graphs provide more accurate results.

        Returns basic dependency analysis using regex patterns.
        For enhanced analysis with AST-accurate relationships, use extract_semantic_analysis().
        """
        if not code:
            return {
                "internal_calls": [],
                "external_imports": [],
                "function_dependencies": {},
            }

        functions = self.extract_functions(tree, code)
        imports = self.extract_imports(tree)

        # Simplified dependency extraction (less accurate than semantic graphs)
        internal_calls = []
        external_imports = set()

        for func in functions:
            func_code = func["complete_code"]
            func_name = func["name"]

            # Basic function call detection (regex-based)
            for other_func in functions:
                if other_func["name"] != func_name:
                    pattern = r"\b" + re.escape(other_func["name"]) + r"\s*\("
                    if re.search(pattern, func_code):
                        internal_calls.append(
                            {
                                "caller": func_name,
                                "callee": other_func["name"],
                                "line": func["line"],
                            }
                        )

            # Basic import usage detection (text-based)
            for imp in imports:
                imp_name = imp["module"]
                if imp_name in func_code:
                    external_imports.add(imp_name)

        return {
            "internal_calls": internal_calls,
            "external_imports": list(external_imports),
            "function_dependencies": {
                func["name"]: [
                    call["callee"]
                    for call in internal_calls
                    if call["caller"] == func["name"]
                ]
                for func in functions
            },
        }

    def extract_semantic_analysis(
        self, tree, source_code: str, file_path: str
    ) -> Dict[str, Any]:
        """
        Enhanced analysis using semantic graphs (combining our approach with friend's approach)
        """
        try:
            # Use the new semantics module for analysis
            semantic_analysis = analyze_semantics(source_code, file_path)

            # Extract semantic graph from the analysis
            if semantic_analysis.get("analysis_type") == "semantic":
                semantic_graph = semantic_analysis.get("semantic_graph", {})
            else:
                semantic_graph = {
                    "nodes": [],
                    "edges": [],
                    "node_metadata": {},
                    "graph_stats": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "functions": 0,
                        "classes": 0,
                        "imports": 0,
                    },
                }

            # Enhance with our existing detailed function extraction
            our_functions = self.extract_functions(tree, source_code)
            our_imports = self.extract_imports(tree)
            our_classes = self.extract_classes(tree)

            # Merge both approaches for comprehensive analysis
            enhanced_analysis = {
                # Our detailed function analysis (with complete code)
                "detailed_functions": our_functions,
                "detailed_imports": our_imports,
                "detailed_classes": our_classes,
                # Semantic analysis from new semantics module
                "function_dependencies": self._extract_function_dependencies(
                    semantic_analysis
                ),
                "import_usage": self._extract_import_usage(semantic_analysis),
                # Graph statistics from semantic graph
                "graph_stats": semantic_graph.get("graph_stats", {}),
                # Additional semantic insights
                "semantic_insights": semantic_analysis.get("semantic_insights", []),
                "security_patterns": semantic_analysis.get("security_patterns", []),
                "function_complexity": semantic_analysis.get("function_complexity", {}),
                # Metadata
                "file_path": file_path,
                "language": self.lang_name,
                "analysis_method": "enhanced_semantic",
            }

            return enhanced_analysis

        except Exception as e:
            print(
                f"Warning: Semantic analysis failed, falling back to basic extraction: {e}"
            )
            # Fallback to our existing methods
            return {
                "detailed_functions": self.extract_functions(tree, source_code),
                "detailed_imports": self.extract_imports(tree),
                "detailed_classes": self.extract_classes(tree),
                "function_dependencies": self.extract_dependencies(tree, source_code)[
                    "function_dependencies"
                ],
                "analysis_method": "fallback_basic",
            }

    def _extract_function_dependencies(
        self, semantic_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Extract function dependencies from semantic analysis"""
        function_dependencies = {}

        if semantic_analysis.get("analysis_type") == "semantic":
            semantic_edges = semantic_analysis.get("semantic_edges", [])

            for edge in semantic_edges:
                if edge.get("relationship") == "calls":
                    source = edge.get("source", "")
                    target = edge.get("target", "")

                    # Extract function names from IDs
                    if source.startswith("func_") and target.startswith("func_"):
                        source_func = source.replace("func_", "").split("_")[0]
                        target_func = target.replace("func_", "").split("_")[0]

                        if source_func not in function_dependencies:
                            function_dependencies[source_func] = []
                        function_dependencies[source_func].append(target_func)

        return function_dependencies

    def _extract_import_usage(
        self, semantic_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Simplified import usage - no longer tracking per-function usage
        since we now provide ALL imported files for comprehensive context.
        """
        return {}  # Empty dict since comprehensive imports provide all context
