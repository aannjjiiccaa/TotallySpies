import ast

class URLExtractor(ast.NodeVisitor):
    def __init__(self):
        self.assignments = {} 

    def visit_Assign(self, node):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                self.assignments[var_name] = node.value.value
            elif isinstance(node.value, ast.Str): 
                self.assignments[var_name] = node.value.s
        self.generic_visit(node)

    def extract_url(self, call_node):
        if not isinstance(call_node, ast.Call):
            return None
        if not call_node.args:
            return None

        arg = call_node.args[0]

        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
        if isinstance(arg, ast.Str):
            return arg.s
        if isinstance(arg, ast.Name):
            return self.assignments.get(arg.id, "dynamic")
        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
            if arg.func.attr == "getenv":
                if arg.args and isinstance(arg.args[0], (ast.Constant, ast.Str)):
                    val = arg.args[0].value if isinstance(arg.args[0], ast.Constant) else arg.args[0].s
                    return f"ENV:{val}"

        return "dynamic"
