import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
import tree_sitter_go as tsgo
import tree_sitter_rust as tsrust
from tree_sitter import Language, Parser, Query, QueryCursor

class MultiLanguageAnalyzer:
    LANGUAGES = {
        'python': tspython,
        'javascript': tsjs,
        'typescript': tsts,
        'go': tsgo,
        'rust': tsrust
    }

    def __init__(self, language: str = 'python'):
        if language not in self.LANGUAGES:
            raise ValueError(f"Unsupported: {language}")
        lang_module = self.LANGUAGES[language]
        self.language = Language(lang_module.language())
        self.parser = Parser(self.language)
        self.lang_name = language

    def parse_code(self, code: str):
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree

    def extract_functions(self, tree):
        queries = {
            'python': """
                (function_definition
                    name: (identifier) @function.name
                )
            """,
            'javascript': """
                (function_declaration
                    name: (identifier) @function.name
                )
                (arrow_function) @function.name
            """,
            'typescript': """
                (function_declaration
                    name: (identifier) @function.name
                )
                (method_definition
                    name: (property_identifier) @function.name
                )
            """,
            'go': """
                (function_declaration
                    name: (identifier) @function.name
                )
                (method_declaration
                    name: (field_identifier) @function.name
                )
            """,
            'rust': """
                (function_item
                    name: (identifier) @function.name
                )
            """
        }
        query = Query(self.language, queries[self.lang_name])
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        functions = []
        for capture_name, nodes in captures.items():
            if "function.name" in capture_name:
                for node in nodes:
                    functions.append({
                        "name": node.text.decode('utf8'),
                        "line": node.start_point[0] + 1,
                        "start_byte": node.start_byte,
                        "end_byte": node.end_byte
                    })
        return functions

    def extract_classes(self, tree):
        queries = {
            'python': """(class_definition name: (identifier) @class.name)""",
            'javascript': """(class_declaration name: (identifier) @class.name)""",
            'typescript': """
                (class_declaration name: (type_identifier) @class.name)
                (interface_declaration name: (type_identifier) @class.name)
            """,
            'go': """(type_declaration (type_spec name: (type_identifier) @class.name))""",
            'rust': """
                (struct_item name: (type_identifier) @class.name)
                (enum_item name: (type_identifier) @class.name)
            """
        }
        query = Query(self.language, queries[self.lang_name])
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        classes = []
        for capture_name, nodes in captures.items():
            if "class.name" in capture_name:
                for node in nodes:
                    classes.append({
                        "name": node.text.decode('utf8'),
                        "line": node.start_point[0] + 1
                    })
        return classes

    def extract_imports(self, tree):
        query = Query(
            self.language,
            """
            (import_statement
                name: (dotted_name) @import.module
            )
            (import_from_statement
                module_name: (dotted_name) @import.from
            )
            """
        )
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        imports = []
        for capture_name, nodes in captures.items():
            for node in nodes:
                imports.append({
                    "module": node.text.decode('utf8'),
                    "line": node.start_point[0] + 1,
                    "type": "from" if "from" in capture_name else "direct"
                })
        return imports

    def find_complex_conditions(self, tree):
        query = Query(
            self.language,
            """
            (if_statement
                condition: (boolean_operator) @complex.condition
            )
            """
        )
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        complex_ifs = []
        for capture_name, nodes in captures.items():
            for node in nodes:
                complex_ifs.append({
                    "condition": node.text.decode('utf8'),
                    "line": node.start_point[0] + 1
                })
        return complex_ifs

    def find_eval_usage(self, tree):
        query = Query(
            self.language,
            """
            (call
                function: (identifier) @func.name
                (#eq? @func.name "eval")
            )
            """
        )
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        eval_calls = []
        for capture_name, nodes in captures.items():
            for node in nodes:
                eval_calls.append({
                    "line": node.start_point[0] + 1,
                    "text": node.text.decode('utf8')
                })
        return eval_calls

    def analyze_file(self, file_path: str):
        with open(file_path, 'r') as f:
            code = f.read()

        tree = self.parse_code(code)

        return {
            "functions": self.extract_functions(tree),
            "classes": self.extract_classes(tree),
            "imports": self.extract_imports(tree),
            "complex_conditions": self.find_complex_conditions(tree),
            "eval_usage": self.find_eval_usage(tree)
        }
