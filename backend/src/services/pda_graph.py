# # src/services/pdg_builder.py - CORRECTLY FIXED FOR TREE-SITTER STRUCTURE

# from tree_sitter import Node
# from typing import Dict, List, Set, Tuple, Optional
# from dataclasses import dataclass, field

# @dataclass
# class PDGNode:
#     """Node in Program Dependence Graph"""
#     id: int
#     code: str
#     line: int
#     node_type: str
#     data_deps: List[tuple[str, int]] = field(default_factory=list)
#     control_deps: List[tuple[int, str]] = field(default_factory=list)
#     defines: Set[str] = field(default_factory=set)
#     uses: Set[str] = field(default_factory=set)

# class PDGBuilder:
#     """Building Program Dependencies Graph from tree-sitter AST"""

#     def __init__(self, language: str = 'python'):
#         self.language = language
#         self.nodes: Dict[int, PDGNode] = {}
#         self.current_id = 0
#         self.var_definitions: Dict[str, int] = {}
#         self.control_stack: List[Tuple[int, str]] = []

#     def build_pdg(self, tree) -> Dict[int, PDGNode]:
#         self._visit(tree.root_node)
#         return self.nodes

#     def _create_node(self, code: str, line: int, node_type: str) -> PDGNode:
#         """Create a new PDG node"""
#         node = PDGNode(
#             id=self.current_id,
#             code=code,
#             line=line,
#             node_type=node_type
#         )

#         for ctrl_id, branch in self.control_stack:
#             node.control_deps.append((ctrl_id, branch))

#         self.nodes[self.current_id] = node
#         self.current_id += 1
#         return node

#     def _visit(self, node: Node):
#         """Recursively visit tree-sitter nodes"""

#         if node.type == 'expression_statement':
#             for child in node.children:
#                 if child.type == 'assignment':
#                     self._handle_assignment(child)
#                     return

#         elif node.type == 'assignment':
#             self._handle_assignment(node)
#             return

#         elif node.type == 'if_statement':
#             self._handle_if_statement(node)
#             return

#         elif node.type == 'while_statement':
#             self._handle_while_statement(node)
#             return

#         elif node.type == 'for_statement':
#             self._handle_for_statement(node)
#             return

#         elif node.type == 'return_statement':
#             self._handle_return(node)
#             return

#         elif node.type == 'function_definition':
#             self._handle_function(node)
#             return

#         for child in node.children:
#             self._visit(child)

#     def _handle_assignment(self, node: Node):
#         """
#         Handles assignment based on actual tree-sitter structure:
#         """

#         code = node.text.decode('utf8')[:50]
#         pdg_node = self._create_node(code, node.start_point[0] + 1, 'assignment')

#         children = list(node.children)

#         if len(children) >= 3:
#             left_node = children[0]
#             if left_node.type == 'identifier':
#                 defined_var = left_node.text.decode('utf8')
#                 print(f"   Defined: {defined_var}")
#                 pdg_node.defines.add(defined_var)
#                 self.var_definitions[defined_var] = pdg_node.id

#             found_equals = False
#             for child in children:
#                 if child.text.decode('utf8') == '=':
#                     found_equals = True
#                     continue

#                 if found_equals:
#                     used_vars = self._extract_identifiers(child)
#                     for var in used_vars:
#                         pdg_node.uses.add(var)
#                         if var in self.var_definitions:
#                             defining_node_id = self.var_definitions[var]
#                             pdg_node.data_deps.append((var, defining_node_id))

#     def _handle_if_statement(self, node: Node):
#         """
#         Handles if statement structure:
#         """

#         code = node.text.decode('utf8')[:50]
#         condition_node = self._create_node(code, node.start_point[0] + 1, 'if_condition')
#         condition = None
#         consequence = None
#         alternative = None

#         for child in node.children:
#             if child.type in ['comparison_operator', 'binary_operator', 'boolean_operator']:
#                 condition = child
#             elif child.type == 'block':
#                 if consequence is None:
#                     consequence = child
#                 else:
#                     alternative = child
#             elif child.type == 'else_clause':
#                 for subchild in child.children:
#                     if subchild.type == 'block':
#                         alternative = subchild

#         # Extract variables from condition
#         if condition:
#             used_vars = self._extract_identifiers(condition)
#             for var in used_vars:
#                 condition_node.uses.add(var)
#                 if var in self.var_definitions:
#                     condition_node.data_deps.append((var, self.var_definitions[var]))

#         # Process true branch
#         if consequence:
#             self.control_stack.append((condition_node.id, 'true'))
#             for child in consequence.children:
#                 self._visit(child)
#             self.control_stack.pop()

#         # Process false branch (else)
#         if alternative:
#             self.control_stack.append((condition_node.id, 'false'))
#             for child in alternative.children:
#                 self._visit(child)
#             self.control_stack.pop()

#     def _handle_while_statement(self, node: Node):
#         """Handles while loop"""

#         code = node.text.decode('utf8')[:50]
#         loop_node = self._create_node(code, node.start_point[0] + 1, 'while_loop')
#         condition = None
#         body = None

#         for child in node.children:
#             if child.type in ['comparison_operator', 'binary_operator']:
#                 condition = child
#             elif child.type == 'block':
#                 body = child

#         if condition:
#             used_vars = self._extract_identifiers(condition)
#             for var in used_vars:
#                 loop_node.uses.add(var)
#                 if var in self.var_definitions:
#                     loop_node.data_deps.append((var, self.var_definitions[var]))

#         if body:
#             self.control_stack.append((loop_node.id, 'true'))
#             for child in body.children:
#                 self._visit(child)
#             self.control_stack.pop()

#     def _handle_for_statement(self, node: Node):
#         """Handles for loop"""

#         code = node.text.decode('utf8')[:50]
#         loop_node = self._create_node(code, node.start_point[0] + 1, 'for_loop')
#         children = list(node.children)
#         found_for = False
#         found_in = False

#         for child in children:
#             if child.text.decode('utf8') == 'for':
#                 found_for = True
#             elif child.text.decode('utf8') == 'in':
#                 found_in = True
#             elif found_for and not found_in and child.type == 'identifier':
#                 # This is the loop variable
#                 loop_var = child.text.decode('utf8')
#                 loop_node.defines.add(loop_var)
#                 self.var_definitions[loop_var] = loop_node.id
#             elif found_in and child.type == 'identifier':
#                 # This is the iterable
#                 used_vars = self._extract_identifiers(child)
#                 for var in used_vars:
#                     loop_node.uses.add(var)
#                     if var in self.var_definitions:
#                         loop_node.data_deps.append((var, self.var_definitions[var]))
#             elif child.type == 'block':
#                 # Process body
#                 self.control_stack.append((loop_node.id, 'true'))
#                 for subchild in child.children:
#                     self._visit(subchild)
#                 self.control_stack.pop()

#     def _handle_return(self, node: Node):
#         """
#         Handles return statement:
#         """

#         code = node.text.decode('utf8')[:50]
#         return_node = self._create_node(code, node.start_point[0] + 1, 'return')

#         # Extracting all identifiers after 'return' keyword
#         found_return = False
#         for child in node.children:
#             if child.text.decode('utf8') == 'return':
#                 found_return = True
#                 continue

#             if found_return:
#                 used_vars = self._extract_identifiers(child)
#                 for var in used_vars:
#                     return_node.uses.add(var)
#                     if var in self.var_definitions:
#                         return_node.data_deps.append((var, self.var_definitions[var]))

#     def _handle_function(self, node: Node):
#         # Getting function name
#         func_name = '<anonymous>'
#         for child in node.children:
#             if child.type == 'identifier':
#                 func_name = child.text.decode('utf8')
#                 break

#         code = f"def {func_name}(...)"
#         func_node = self._create_node(code, node.start_point[0] + 1, 'function')

#         # Getting parameters
#         for child in node.children:
#             if child.type == 'parameters':
#                 for param_child in child.children:
#                     if param_child.type == 'identifier':
#                         param = param_child.text.decode('utf8')
#                         func_node.defines.add(param)
#                         self.var_definitions[param] = func_node.id

#         # Processing body
#         for child in node.children:
#             if child.type == 'block':
#                 for subchild in child.children:
#                     self._visit(subchild)

#     def _extract_identifiers(self, node: Node) -> Set[str]:
#         """Recursively extracting all identifier names from a node"""
#         identifiers = set()
#         def walk(n):
#             if n.type == 'identifier':
#                 identifiers.add(n.text.decode('utf8'))
#             for child in n.children:
#                 walk(child)

#         walk(node)
#         return identifiers
