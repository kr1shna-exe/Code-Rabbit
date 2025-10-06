# from tree_sitter import Node
# from typing import Dict,List
# from dataclasses import dataclass, field

# @dataclass
# class CFGNode:
#     id: int
#     code: str
#     line: int
#     node_type: str
#     successors: List[int] = field(default_factory=list)
#     predecessors: List[int] = field(default_factory=list)

# class TreeSitterCFGBuilder:

#     CONTROL_NODES = {
#         'python': ['if_statement', 'while_statement', 'for_statement', 'match_statement'],
#         'javascript': ['if_statement', 'while_statement', 'for_statement', 'switch_statement'],
#         'typescript': ['if_statement', 'while_statement', 'for_statement', 'switch_statement'],
#         'go': ['if_statement', 'for_statement', 'switch_statement'],
#         'rust': ['if_expression', 'while_expression', 'for_expression', 'match_expression']
#     }

#     def __init__(self, language: str):
#         self.language = language
#         self.nodes: Dict[int, CFGNode] = {}
#         self.current_id = 0

#     def build_cfg(self, tree):
#         entry = self._create_node('<entry>', 0, 'entry')
#         exit_node = self._create_node('<exit>', 0, 'exit')

#         last_nodes = self._visit(tree.root_node, [entry.id])
#         for node_id in last_nodes:
#             self._add_edge(node_id, exit_node.id)
#         return self.nodes

#     def _create_node(self, code: str, line: int, node_type: str):
#         node = CFGNode(self.current_id, code, line, node_type)
#         self.nodes[self.current_id] = node
#         self.current_id += 1
#         return node

#     def _add_edge(self, from_id: int, to_id: int):
#         self.nodes[from_id].successors.append(to_id)
#         self.nodes[to_id].predecessors.append(from_id)

#     def _visit(self, node: Node, predecessors: List[int]):
#         control_types = self.CONTROL_NODES.get(self.language, [])

#         if node.type in control_types:
#             return self._handle_control_node(node, predecessors)

#         if node.child_count == 0 or self._is_statement(node):
#             stmt_node = self._create_node(
#                 node.text.decode('utf8')[:50],
#                 node.start_point[0] + 1,
#                 node.type
#             )
#             for pred in predecessors:
#                 self._add_edge(pred, stmt_node.id)
#             return [stmt_node.id]

#         current_preds = predecessors
#         for child in node.children:
#             current_preds = self._visit(child, current_preds)

#         return current_preds

#     def _handle_control_node(self, node: Node, predecessors: List[int]) -> List[int]:
#         cond_node = self._create_node(
#             node.text.decode('utf8')[:50],
#             node.start_point[0] + 1,
#             node.type
#         )
#         for pred in predecessors:
#             self._add_edge(pred, cond_node.id)

#         branches = []
#         for child in node.children:
#             if child.type == 'block' or child.type in ['consequence', 'alternative']:
#                 branch_preds = self._visit(child, [cond_node.id])
#                 branches.extend(branch_preds)

#         if not branches:
#             return [cond_node.id]

#         return branches

#     def _is_statement(self, node: Node) -> bool:
#         statement_types = {
#             'python': ['expression_statement', 'assignment', 'return_statement'],
#             'javascript': ['expression_statement', 'variable_declaration', 'return_statement'],
#             'typescript': ['expression_statement', 'variable_declaration', 'return_statement'],
#             'go': ['expression_statement', 'assignment_statement', 'return_statement'],
#             'rust': ['expression_statement', 'let_declaration', 'return_expression']
#         }
#         return node.type in statement_types.get(self.language, [])