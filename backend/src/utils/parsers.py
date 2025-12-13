import ast
import os

def detect_language(file_path):
    file_path = str(file_path)
    if file_path.endswith(".py"):
        return "python"
    elif file_path.endswith(".c"):
        return "c"
    elif file_path.endswith(".cpp"):
        return "cpp"
    elif file_path.endswith(".java"):
        return "java"
    else:
        return "unknown"

def parse_python(file_path):
    imports = set()
    defined = set()
    used = set()

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                module_name = n.name
                abs_path = resolve_import_from_file(file_path, module_name)
                imports.add(abs_path if abs_path else module_name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                abs_path = resolve_import_from_file(file_path, node.module)
                imports.add(abs_path if abs_path else node.module)

        elif isinstance(node, ast.ClassDef):
            defined.add(node.name)

        elif isinstance(node, ast.FunctionDef):
            defined.add(node.name)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used.add(node.func.id)

    return {
        "language": "python",
        "imports": list(imports),
        "symbols_defined": list(defined),
        "symbols_used": list(used)
    }


def resolve_import_from_file(current_file_path, module_name):
    base_dir = os.path.dirname(os.path.abspath(current_file_path))
    parts = module_name.split(".") 
    search_dir = base_dir
    while True:
        candidate = os.path.join(search_dir, *parts) 
        py_file = candidate + ".py"                 
        
        if os.path.isfile(py_file):
            return os.path.abspath(py_file)
        elif os.path.isfile(os.path.join(candidate, "__init__.py")):
            return os.path.abspath(os.path.join(candidate, "__init__.py"))
        
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent
    
    return None

