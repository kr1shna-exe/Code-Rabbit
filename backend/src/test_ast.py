from services.ast_parser import MultiLanguageAnalyzer
from services.code_graph import TreeSitterCFGBuilder
from services.graph_visualizer import GraphVisualizer

print("Python Code Test")
py_analyzer = MultiLanguageAnalyzer('python')
py_tree = py_analyzer.parse_code("""
def calculate(x):
    if x > 0:
        return x * 2
    return 0
""")

functions = py_analyzer.extract_functions(py_tree)
print(f"Functions: {functions}")

cfg_builder = TreeSitterCFGBuilder('python')
cfg = cfg_builder.build_cfg(py_tree)
print(f"CFG nodes: {len(cfg)}")

visualizer = GraphVisualizer(cfg)
visualizer.generate_dot("python_cfg.dot")

print("\nCFG Structure:")
for node_id, node in cfg.items():
    print(f"  Node {node_id} ({node.node_type}): {node.code[:30]}")
    if node.successors:
        print(f"    → Flows to: {node.successors}")

print("\nJavaScript Code Test")
js_analyzer = MultiLanguageAnalyzer('javascript')
js_tree = js_analyzer.parse_code("""
function hello(name) {
    if (name) {
        return `Hello ${name}`;
    }
    return 'Hello';
}
""")

functions = js_analyzer.extract_functions(js_tree)
print(f"Functions: {functions}")

cfg_builder = TreeSitterCFGBuilder('javascript')
cfg = cfg_builder.build_cfg(js_tree)
print(f"CFG nodes: {len(cfg)}")

visualizer = GraphVisualizer(cfg)
visualizer.generate_dot("javascript_cfg.dot")

print("\nDone.Check python_cfg.dot and javascript_cfg.dot")
