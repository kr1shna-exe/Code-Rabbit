from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class SemanticNode:
    """Represents a semantic node in the code graph"""

    id: str
    name: str
    type: str  # function, class, import, call_target, file
    file_path: str
    line: int
    span: Tuple[tuple[int, int], Tuple[int, int]]
    code: Optional[str] = None
    parameters: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dictioinary)


class SemanticGraphBuilder:
    """
    Build semantic code graphs from AST using NetworkX.
    Based on friend's approach but integrated with our AST parser.
    """

    def __init__(self, language: str):
        self.language = language
        self.graph = nx.DiGraph()
        # Import here to avoid circular dependency
        from .ast_parser import MultiLanguageAnalyzer

        self.ast_parser = MultiLanguageAnalyzer(language)
        self.current_definitions: List[str] = []  # Track current scope (function/class)
        self.file_path: str = ""

    def build_semantic_graph(
        self, tree, source_code: bytes, file_path: str
    ) -> nx.DiGraph:
        """
        Build a semantic graph from AST with:
        - Nodes: functions, classes, imports, call targets
        - Edges: defines, calls, imports, contains relationships
        """
        self.graph = nx.DiGraph()
        self.file_path = file_path
        self.source_code = source_code

        # Add file anchor node
        file_node_id = f"{file_path}::file"
        self._add_node(
            node_id=file_node_id,
            name=file_path,
            node_type="file",
            line=1,
            span=((0, 0), (0,)),
        )

        # Walk the AST and build semantic relationships
        self._walk_ast(tree.root_node)

        return self.graph

    def _walk_ast(self, node, current_def: Optional[str] = None):
        """Recursively walk AST nodes and build semantic relationships"""

        # Track current definition scope
        original_def = current_def

        # Handle definitions (functions, classes)
        if self.language == "python":
            current_def = self._handle_python_definitions(node, current_def)
        elif self.language in ["javascript", "typescript"]:
            current_def = self._handle_js_ts_definitions(node, current_def)
        elif self.language == "go":
            current_def = self._handle_go_definitions(node, current_def)

        # Handle imports
        self._handle_imports(node, current_def)

        # Handle function calls
        self._handle_function_calls(node, current_def)

        # Recursively process children
        for child in node.children:
            self._walk_ast(child, current_def)

        # Restore original scope
        current_def = original_def

    def _handle_python_definitions(
        self, node, current_def: Optional[str]
    ) -> Optional[str]:
        """Handle Python function and class definitions"""
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self._get_node_text(name_node)
                params_node = node.child_by_field_name("parameters")
                params = self._get_node_text(params_node) if params_node else ""

                def_id = self._add_definition(
                    name=name, node_type="function", ast_node=node, parameters=params
                )

                # Add contains relationship if we're inside another definition
                if current_def:
                    self._add_edge(current_def, def_id, "contains")

                return def_id

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self._get_node_text(name_node)

                class_id = self._add_definition(
                    name=name, node_type="class", ast_node=node
                )

                if current_def:
                    self._add_edge(current_def, class_id, "contains")

                return class_id

        return current_def

    def _handle_js_ts_definitions(
        self, node, current_def: Optional[str]
    ) -> Optional[str]:
        """Handle JavaScript/TypeScript function and class definitions"""
        if node.type in ["function_declaration", "method_definition"]:
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self._get_node_text(name_node)
                params_node = node.child_by_field_name("parameters")
                params = self._get_node_text(params_node) if params_node else ""

                def_id = self._add_definition(
                    name=name, node_type="function", ast_node=node, parameters=params
                )

                if current_def:
                    self._add_edge(current_def, def_id, "contains")

                return def_id

        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self._get_node_text(name_node)

                class_id = self._add_definition(
                    name=name, node_type="class", ast_node=node
                )

                if current_def:
                    self._add_edge(current_def, class_id, "contains")

                return class_id

        return current_def

    def _handle_go_definitions(self, node, current_def: Optional[str]) -> Optional[str]:
        """Handle Go function and type definitions"""
        if node.type in ["function_declaration", "method_declaration"]:
            name_node = node.child_by_field_name("name")
            if name_node:
                name = self._get_node_text(name_node)
                params_node = node.child_by_field_name("parameters")
                params = self._get_node_text(params_node) if params_node else ""

                def_id = self._add_definition(
                    name=name, node_type="function", ast_node=node, parameters=params
                )

                if current_def:
                    self._add_edge(current_def, def_id, "contains")

                return def_id

        return current_def

    def _handle_imports(self, node, current_def: Optional[str]):
        """Handle import statements and create import nodes"""
        if self.language == "python":
            if node.type in ["import_statement", "import_from_statement"]:
                import_text = self._get_node_text(node).strip()
                import_id = f"{self.file_path}::import::{import_text}"

                self._add_node(
                    node_id=import_id,
                    name=import_text,
                    node_type="import",
                    line=node.start_point[0] + 1,
                    span=(node.start_point, node.end_point),
                    metadata={"code": import_text},
                )

                # Connect to containing function or file
                if current_def:
                    self._add_edge(current_def, import_id, "uses_import")
                else:
                    file_id = f"{self.file_path}::file"
                    self._add_edge(file_id, import_id, "imports")

        elif self.language in ["javascript", "typescript"]:
            if node.type == "import_statement":
                # Extract module name from import statement
                for child in node.children:
                    if child.type == "string":
                        module_name = self._get_node_text(child).strip("\"'")
                        import_id = f"{self.file_path}::import::{module_name}"

                        self._add_node(
                            node_id=import_id,
                            name=module_name,
                            node_type="import",
                            line=node.start_point[0] + 1,
                            span=(node.start_point, node.end_point),
                            metadata={"code": module_name},
                        )

                        if current_def:
                            self._add_edge(current_def, import_id, "uses_import")
                        else:
                            file_id = f"{self.file_path}::file"
                            self._add_edge(file_id, import_id, "imports")
                        break

    def _handle_function_calls(self, node, current_def: Optional[str]):
        """Handle function calls and create call relationships"""
        if self.language == "python" and node.type == "call":
            func_node = None
            if node.child_by_field_name("function"):
                func_node = node.child_by_field_name("function")
            elif len(node.children) > 0:
                func_node = node.children[0]

            if func_node and current_def:
                called_name = self._get_node_text(func_node).split("(")[0].strip()
                if called_name:
                    call_id = f"{self.file_path}::call::{called_name}"

                    self._add_node(
                        node_id=call_id,
                        name=called_name,
                        node_type="call_target",
                        line=node.start_point[0] + 1,
                        span=(node.start_point, node.end_point),
                    )

                    self._add_edge(current_def, call_id, "calls")

        elif (
            self.language in ["javascript", "typescript"]
            and node.type == "call_expression"
        ):
            # Find the function being called
            for child in node.children:
                if child.type in ["identifier", "member_expression"]:
                    called_name = self._get_node_text(child).split("(")[0].strip()
                    if called_name and current_def:
                        call_id = f"{self.file_path}::call::{called_name}"

                        self._add_node(
                            node_id=call_id,
                            name=called_name,
                            node_type="call_target",
                            line=node.start_point[0] + 1,
                            span=(node.start_point, node.end_point),
                        )

                        self._add_edge(current_def, call_id, "calls")
                    break

    def _add_definition(
        self, name: str, node_type: str, ast_node, parameters: str = ""
    ) -> str:
        """Add a function or class definition to the graph"""
        def_id = f"{self.file_path}::{node_type}::{name}"

        self._add_node(
            node_id=def_id,
            name=name,
            node_type=node_type,
            line=ast_node.start_point[0] + 1,
            span=(ast_node.start_point, ast_node.end_point),
            code=self._get_node_text(ast_node),
            parameters=parameters,
        )

        return def_id

    def _add_node(
        self,
        node_id: str,
        name: str,
        node_type: str,
        line: int,
        span: Tuple[Tuple[int, int], Tuple[int, int]],
        code: Optional[str] = None,
        parameters: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add a node to the semantic graph"""
        self.graph.add_node(
            node_id,
            name=name,
            type=node_type,
            file_path=self.file_path,
            line=line,
            span=span,
            code=code,
            parameters=parameters,
            metadata=metadata or {},
        )

    def _add_edge(self, from_id: str, to_id: str, edge_type: str):
        """Add a typed edge to the semantic graph"""
        self.graph.add_edge(from_id, to_id, type=edge_type)

    def _get_node_text(self, node) -> str:
        """Extract text from an AST node"""
        if node is None:
            return ""
        try:
            return self.source_code[node.start_byte : node.end_byte].decode("utf-8")
        except Exception:
            return ""

    def get_function_dependencies(self) -> Dict[str, List[str]]:
        """Extract function dependencies from the semantic graph"""
        dependencies = {}

        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == "function":
                func_name = node_data["name"]
                dependencies[func_name] = []

                # Find all outgoing edges (calls this function makes)
                for _, target_id, edge_data in self.graph.out_edges(node_id, data=True):
                    if edge_data["type"] == "calls":
                        target_node = self.graph.nodes[target_id]
                        dependencies[func_name].append(target_node["name"])

        return dependencies

    def get_import_usage(self) -> Dict[str, List[str]]:
        """Extract which functions use which imports"""
        import_usage = {}

        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == "function":
                func_name = node_data["name"]
                import_usage[func_name] = []

                # Find all imports used by this function
                for _, target_id, edge_data in self.graph.out_edges(node_id, data=True):
                    if edge_data["type"] == "uses_import":
                        import_node = self.graph.nodes[target_id]
                        import_usage[func_name].append(import_node["name"])

        return import_usage

    def to_analysis_dict(self) -> Dict[str, Any]:
        """Convert semantic graph to analysis dictionary for context building"""
        functions = []
        classes = []
        imports = []

        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == "function":
                functions.append(
                    {
                        "name": node_data["name"],
                        "line": node_data["line"],
                        "parameters": node_data.get("parameters", ""),
                        "code": node_data.get("code", ""),
                        "span": node_data["span"],
                    }
                )
            elif node_data["type"] == "class":
                classes.append(
                    {
                        "name": node_data["name"],
                        "line": node_data["line"],
                        "span": node_data["span"],
                    }
                )
            elif node_data["type"] == "import":
                imports.append(
                    {
                        "module": node_data["name"],
                        "line": node_data["line"],
                        "type": "direct",
                    }
                )

        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "dependencies": self.get_function_dependencies(),
            "import_usage": self.get_import_usage(),
            "graph_stats": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "functions": len(functions),
                "classes": len(classes),
                "imports": len(imports),
            },
        }
