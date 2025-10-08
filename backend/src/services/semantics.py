import ast
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SemanticNode:
    """Represents a semantic node in the code analysis graph"""

    id: str
    type: str
    name: str
    line: int
    file_path: str
    metadata: Dict[str, Any]


@dataclass
class SemanticEdge:
    """Represents a semantic relationship between nodes"""

    source: str
    target: str
    relationship: str
    line: int
    metadata: Dict[str, Any] = None


class SemanticAnalyzer:
    """
    Advanced semantics that understands
    the deeper meaning and relationships in code.
    """

    def __init__(self):
        self.nodes: List[SemanticNode] = []
        self.edges: List[SemanticEdge] = []
        self.variable_types: Dict[str, str] = {}
        self.function_complexity: Dict[str, int] = {}
        self.security_patterns: List[Dict[str, Any]] = []
        self.imports_map = {}  # Simple import_name -> module mapping
        self.function_calls = []  # Simple function call tracking

    def analyze_code_semantics(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis of code
        """
        try:
            tree = ast.parse(code)

            # Clear previous analysis
            self.nodes.clear()
            self.edges.clear()
            self.variable_types.clear()
            self.function_complexity.clear()
            self.security_patterns.clear()
            self.imports_map.clear()
            self.function_calls.clear()

            # Perform semantic analysis
            self._analyze_functions(tree, file_path)
            self._analyze_classes(tree, file_path)
            self._analyze_imports(tree, file_path)
            self._detect_security_patterns(tree, file_path)
            self._calculate_complexity_metrics(tree, file_path)

            # Build semantic graph
            semantic_graph = self._build_semantic_graph()

            return {
                "semantic_nodes": [node.__dict__ for node in self.nodes],
                "semantic_edges": [edge.__dict__ for edge in self.edges],
                "semantic_graph": semantic_graph,
                "variable_types": self.variable_types,
                "function_complexity": self.function_complexity,
                "security_patterns": self.security_patterns,
                "imports_map": self.imports_map,  # Simple import mapping
                "function_calls": self.function_calls,  # Simple function call tracking
                "analysis_type": "semantic",
                "semantic_insights": self._extract_semantic_insights(),
            }

        except SyntaxError as e:
            return {
                "error": f"Syntax error in {file_path}: {str(e)}",
                "analysis_type": "semantic_failed",
            }
        except Exception as e:
            return {
                "error": f"Semantic analysis failed for {file_path}: {str(e)}",
                "analysis_type": "semantic_failed",
            }

    def _analyze_functions(self, tree: ast.AST, file_path: str):
        """Analyze functions and their semantic relationships"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Create semantic node for function
                func_node = SemanticNode(
                    id=f"func_{node.name}_{file_path}",
                    type="function",
                    name=node.name,
                    line=node.lineno,
                    file_path=file_path,
                    metadata={
                        "signature": self._get_function_signature(node),
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "returns": self._get_return_annotation(node),
                        "decorators": [
                            self._get_decorator_name(d) for d in node.decorator_list
                        ],
                    },
                )
                self.nodes.append(func_node)

                # Analyze function calls within this function
                self._analyze_function_calls(node, func_node, file_path)

    def _analyze_classes(self, tree: ast.AST, file_path: str):
        """Analyze classes and their semantic relationships"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Create semantic node for class
                class_node = SemanticNode(
                    id=f"class_{node.name}_{file_path}",
                    type="class",
                    name=node.name,
                    line=node.lineno,
                    file_path=file_path,
                    metadata={
                        "bases": [
                            self._get_base_class_name(base) for base in node.bases
                        ],
                        "methods": [
                            n.name for n in node.body if isinstance(n, ast.FunctionDef)
                        ],
                        "docstring": ast.get_docstring(node),
                    },
                )
                self.nodes.append(class_node)

                # Analyze inheritance relationships
                for base in node.bases:
                    base_name = self._get_base_class_name(base)
                    if base_name:
                        edge = SemanticEdge(
                            source=class_node.id,
                            target=f"class_{base_name}_{file_path}",
                            relationship="inherits",
                            line=node.lineno,
                        )
                        self.edges.append(edge)

                # Analyze method relationships
                self._analyze_class_methods(node, class_node, file_path)

    def _analyze_imports(self, tree: ast.AST, file_path: str):
        """Analyze imports and create simple import mapping"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Simple mapping: import_name -> module_name
                    import_name = alias.asname or alias.name
                    self.imports_map[import_name] = alias.name

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    # Simple mapping: function_name -> module_name
                    self.imports_map[alias.name] = module

    def _detect_security_patterns(self, tree: ast.AST, file_path: str):
        """Detect potential security patterns and vulnerabilities"""
        security_issues = []

        for node in ast.walk(tree):
            # Check for hardcoded secrets
            if isinstance(node, ast.Str) and self._is_potential_secret(node.s):
                security_issues.append(
                    {
                        "type": "hardcoded_secret",
                        "line": node.lineno,
                        "value": node.s[:50] + "..." if len(node.s) > 50 else node.s,
                        "severity": "high",
                    }
                )

            # Check for eval/exec usage
            elif isinstance(node, ast.Call) and self._is_eval_risk(node):
                security_issues.append(
                    {
                        "type": "eval_usage",
                        "line": node.lineno,
                        "function": self._get_call_name(node),
                        "severity": "high",
                    }
                )

        self.security_patterns = security_issues

    def _calculate_complexity_metrics(self, tree: ast.AST, file_path: str):
        """Calculate cyclomatic complexity and other metrics"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_function_complexity(node)
                self.function_complexity[node.name] = complexity

    def _build_semantic_graph(self) -> Dict[str, Any]:
        """Build the semantic graph representation"""
        return {
            "nodes": [node.id for node in self.nodes],
            "edges": [(edge.source, edge.target) for edge in self.edges],
            "node_metadata": {node.id: node.metadata for node in self.nodes},
            "graph_stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "functions": len([n for n in self.nodes if n.type == "function"]),
                "classes": len([n for n in self.nodes if n.type == "class"]),
                "imports": len([n for n in self.nodes if n.type == "import"]),
            },
        }

    def _extract_semantic_insights(self) -> List[Dict[str, Any]]:
        """Extract high-level semantic insights from the analysis"""
        insights = []

        # Analyze function complexity
        high_complexity_funcs = [
            name
            for name, complexity in self.function_complexity.items()
            if complexity > 10
        ]
        if high_complexity_funcs:
            insights.append(
                {
                    "type": "high_complexity_functions",
                    "message": f"Functions with high complexity: {', '.join(high_complexity_funcs)}",
                    "severity": "medium",
                }
            )

        # Analyze security patterns
        if self.security_patterns:
            insights.append(
                {
                    "type": "security_concerns",
                    "message": f"Found {len(self.security_patterns)} potential security issues",
                    "severity": "high",
                }
            )

        return insights

    # Helper methods
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature"""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"

    def _get_return_annotation(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation"""
        if node.returns:
            return (
                ast.unparse(node.returns)
                if hasattr(ast, "unparse")
                else str(node.returns)
            )
        return None

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return ast.unparse(decorator) if hasattr(ast, "unparse") else str(decorator)
        return str(decorator)

    def _get_base_class_name(self, base: ast.AST) -> Optional[str]:
        """Get base class name"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return ast.unparse(base) if hasattr(ast, "unparse") else str(base)
        return None

    def _analyze_function_calls(
        self, node: ast.FunctionDef, func_node: SemanticNode, file_path: str
    ):
        """Analyze function calls within a function"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._get_call_name(child)
                if call_name:
                    # Create edge for function call
                    target_id = f"func_{call_name}_{file_path}"
                    edge = SemanticEdge(
                        source=func_node.id,
                        target=target_id,
                        relationship="calls",
                        line=child.lineno,
                        metadata={
                            "call_name": call_name,
                            "is_cross_file": False  # Will be updated by context builder
                        }
                    )
                    self.edges.append(edge)

                    # Simple function call tracking
                    self.function_calls.append({
                        "calling_function": func_node.name,
                        "called_function": call_name,
                        "line": child.lineno,
                        "file_path": file_path
                    })

    def _analyze_class_methods(
        self, node: ast.ClassDef, class_node: SemanticNode, file_path: str
    ):
        """Analyze method relationships within a class"""
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                # Create relationship between class and method
                method_id = f"func_{child.name}_{file_path}"
                edge = SemanticEdge(
                    source=class_node.id,
                    target=method_id,
                    relationship="has_method",
                    line=child.lineno,
                )
                self.edges.append(edge)

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity

    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Get the name of a function call"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return ast.unparse(node.func) if hasattr(ast, "unparse") else str(node.func)
        return None

    def _is_potential_secret(self, value: str) -> bool:
        """Check if a string might be a hardcoded secret"""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
        ]
        return any(
            re.search(pattern, value, re.IGNORECASE) for pattern in secret_patterns
        )

    def _is_eval_risk(self, node: ast.Call) -> bool:
        """Check if a function call uses eval/exec"""
        if isinstance(node.func, ast.Name):
            return node.func.id in ["eval", "exec", "compile"]
        return False

    

def analyze_semantics(code: str, file_path: str) -> Dict[str, Any]:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze_code_semantics(code, file_path)

